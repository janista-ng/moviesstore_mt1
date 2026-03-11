from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum

from cart.models import Item
from cities_light.models import City


def map_view(request):
    return render(request, 'geo/map.html')


def popular_locations(request):
    # Aggregate total purchased quantity per city (using order.city FK)
    qs = (
        Item.objects
        .filter(order__city__isnull=False)
        .values('order__city')
        .annotate(purchase_count=Sum('quantity'))
        .order_by('-purchase_count')
    )

    features = []

    for item in qs:
        city_id = item.get('order__city')
        count = item.get('purchase_count') or 0
        if not city_id:
            continue

        city_obj = City.objects.filter(id=city_id).first()
        if not city_obj:
            continue

        name = getattr(city_obj, 'name', '')
        try:
            lat = float(getattr(city_obj, 'latitude', 0) or 0)
            lon = float(getattr(city_obj, 'longitude', 0) or 0)
        except Exception:
            lat, lon = 0.0, 0.0

        # compute top movies for this city
        top_qs = (
            Item.objects
            .filter(order__city=city_obj)
            .values('movie__id', 'movie__name')
            .annotate(count=Sum('quantity'))
            .order_by('-count')[:5]
        )
        top_movies = [
            {'id': m['movie__id'], 'title': m['movie__name'], 'count': m['count']}
            for m in top_qs
        ]

        props = {
            'city_id': city_id,
            'city_name': name,
            'purchase_count': count,
            'top_movies': top_movies,
        }

        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': props,
        })

    geojson = {'type': 'FeatureCollection', 'features': features}
    return JsonResponse(geojson)
