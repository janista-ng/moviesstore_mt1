"""
Management command to populate the database with sample data:
- Users from different cities
- Movies (uses existing images from movie_images)
- Reviews on movies
- Orders (purchases) from various cities

Run after: python manage.py migrate && python manage.py cities_light
"""

import os
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image

from accounts.models import Profile
from movies.models import Movie, Review
from cart.models import Order, Item
from cities_light.models import City


# Sample movie data
SAMPLE_MOVIES = [
    {"name": "Inception", "price": 1499, "description": "A thief who steals corporate secrets through dream-sharing technology."},
    {"name": "The Dark Knight", "price": 1299, "description": "Batman must accept one of the greatest psychological tests to fight injustice."},
    {"name": "Interstellar", "price": 1599, "description": "A team of explorers travel through a wormhole in space."},
    {"name": "The Matrix", "price": 999, "description": "A computer hacker learns about the true nature of reality."},
    {"name": "Pulp Fiction", "price": 1199, "description": "The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine."},
    {"name": "Forrest Gump", "price": 1099, "description": "The presidencies of Kennedy and Johnson through the eyes of an Alabama man."},
    {"name": "The Shawshank Redemption", "price": 899, "description": "Two imprisoned men bond over a number of years."},
    {"name": "Gladiator", "price": 1299, "description": "A former Roman General seeks justice after being betrayed."},
    {"name": "Avatar", "price": 1499, "description": "A paraplegic Marine dispatched to the moon Pandora."},
    {"name": "Titanic", "price": 999, "description": "A seventeen-year-old aristocrat falls in love with a kind artist."},
    {"name": "The Godfather", "price": 1199, "description": "The aging patriarch of an organized crime dynasty transfers control."},
    {"name": "Fight Club", "price": 1099, "description": "An insomniac office worker forms an underground fight club."},
]

# Sample user data: (username, email, city_name_part) - city matched by name contains
SAMPLE_USERS = [
    ("alice_atlanta", "alice@example.com", "Atlanta"),
    ("bob_boston", "bob@example.com", "Boston"),
    ("carol_chicago", "carol@example.com", "Chicago"),
    ("dave_denver", "dave@example.com", "Denver"),
    ("eve_seattle", "eve@example.com", "Seattle"),
    ("frank_miami", "frank@example.com", "Miami"),
    ("grace_nyc", "grace@example.com", "New York"),
    ("henry_houston", "henry@example.com", "Houston"),
    ("iris_la", "iris@example.com", "Los Angeles"),
    ("jack_phoenix", "jack@example.com", "Phoenix"),
    ("kate_sf", "kate@example.com", "San Francisco"),
    ("leo_dallas", "leo@example.com", "Dallas"),
    ("mia_detroit", "mia@example.com", "Detroit"),
    ("noah_philly", "noah@example.com", "Philadelphia"),
    ("olivia_portland", "olivia@example.com", "Portland"),
]

# Sample review comments
SAMPLE_COMMENTS = [
    "Absolutely loved it! One of the best films I've seen.",
    "Great movie, highly recommend.",
    "Solid film with excellent performances.",
    "A bit overhyped but still enjoyable.",
    "Classic! Never gets old.",
    "Mind-blowing plot twists.",
    "Beautiful cinematography and storytelling.",
    "Could have been shorter but overall good.",
    "Instant favorite. Will watch again!",
    "Surprisingly good. Exceeded my expectations.",
]


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def get_existing_movie_images(media_root):
    """Return list of image filenames in movie_images (excluding placeholders)."""
    img_dir = os.path.join(media_root, "movie_images")
    if not os.path.isdir(img_dir):
        return []
    images = []
    for f in os.listdir(img_dir):
        if f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith("placeholder_"):
            images.append(f"movie_images/{f}")
    return images


def create_placeholder_image(path):
    """Create a simple placeholder image (300x450 poster-ish size)."""
    img = Image.new("RGB", (300, 450), color=(random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "JPEG", quality=85)
    return path


class Command(BaseCommand):
    help = "Populate database with sample users, movies, reviews, and orders"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing sample data before populating (keeps superusers)",
        )
        parser.add_argument(
            "--skip-cities-check",
            action="store_true",
            help="Skip check for cities_light data (use if cities not yet populated)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        if not options["skip_cities_check"]:
            city_count = City.objects.count()
            if city_count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        "No cities found. Run 'python manage.py cities_light' first, then run this command again."
                    )
                )
                return

        if not options["clear"] and (User.objects.count() > 0 or Movie.objects.count() > 0):
            self.stdout.write(
                self.style.WARNING(
                    "Database already has users or movies. Use --clear to replace with sample data."
                )
            )
            return

        self._create_movies()
        self._create_users()
        self._create_reviews()
        self._create_orders()

        self.stdout.write(self.style.SUCCESS("Sample data populated successfully!"))

    def _clear_data(self):
        """Remove sample data (preserve superusers)."""
        self.stdout.write("Clearing existing data...")

        Item.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Movie.objects.all().delete()

        # Delete non-superuser users (and their profiles via CASCADE)
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Cleared."))

    def _create_movies(self):
        """Create sample movies using existing images from movie_images."""
        media_root = settings.MEDIA_ROOT
        existing_images = get_existing_movie_images(media_root)

        for i, data in enumerate(SAMPLE_MOVIES):
            if existing_images:
                img_rel = random.choice(existing_images)
            else:
                img_rel = f"movie_images/placeholder_{i + 1}.jpg"
                img_path = os.path.join(media_root, img_rel)
                if not os.path.exists(img_path):
                    create_placeholder_image(img_path)

            Movie.objects.get_or_create(
                name=data["name"],
                defaults={
                    "price": data["price"],
                    "description": data["description"],
                    "image": img_rel,
                },
            )
        self.stdout.write(f"  Created {len(SAMPLE_MOVIES)} movies.")

    def _create_users(self):
        """Create users with profiles linked to cities."""
        cities = list(City.objects.all())
        if not cities:
            self.stdout.write(self.style.WARNING("  No cities - skipping users."))
            return

        created = 0
        for username, email, city_hint in SAMPLE_USERS:
            if User.objects.filter(username=username).exists():
                continue
            # Find a city matching the hint, or pick random
            city = next((c for c in cities if city_hint.lower() in getattr(c, "name", "").lower()), None)
            if not city:
                city = random.choice(cities)

            user = User.objects.create_user(
                username=username,
                email=email,
                password="samplepass123",
                first_name=username.split("_")[0].capitalize(),
            )
            profile = user.profile
            profile.city = city
            if hasattr(city, "latitude") and city.latitude:
                profile.latitude = city.latitude
            if hasattr(city, "longitude") and city.longitude:
                profile.longitude = city.longitude
            profile.save()
            created += 1

        self.stdout.write(f"  Created {created} users (password: samplepass123).")

    def _create_reviews(self):
        """Create reviews from users on movies."""
        users = list(User.objects.filter(is_superuser=False))
        movies = list(Movie.objects.all())
        if not users or not movies:
            return

        count = 0
        for _ in range(80):  # ~80 reviews
            user = random.choice(users)
            movie = random.choice(movies)
            if Review.objects.filter(movie=movie, user=user).exists():
                continue
            Review.objects.create(
                movie=movie,
                user=user,
                comment=random.choice(SAMPLE_COMMENTS),
                rating=random.randint(1, 5),
            )
            count += 1
        self.stdout.write(f"  Created {count} reviews.")

    def _create_orders(self):
        """Create orders (purchases) from users in different cities."""
        users = list(User.objects.filter(is_superuser=False))
        movies = list(Movie.objects.all())
        if not users or not movies:
            return

        count = 0
        for _ in range(60):  # ~60 orders
            user = random.choice(users)
            profile = getattr(user, "profile", None)
            city = profile.city if profile else None
            if not city:
                continue

            # Random cart: 1-4 movies, random quantities
            cart_movies = random.sample(movies, k=random.randint(1, min(4, len(movies))))
            total = 0
            items_data = []
            for m in cart_movies:
                qty = random.randint(1, 3)
                total += m.price * qty
                items_data.append((m, qty))

            order = Order.objects.create(user=user, total=total, city=city)
            for movie, qty in items_data:
                Item.objects.create(order=order, movie=movie, price=movie.price, quantity=qty)
            count += 1

        self.stdout.write(f"  Created {count} orders (purchases).")
