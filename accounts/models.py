from django.db import models
from django.conf import settings
from cities_light.models import City


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
	latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

	def __str__(self):
		return f"Profile({self.user.username})"
