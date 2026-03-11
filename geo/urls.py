from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.map_view, name='geo-map'),
    path('popular_locations.json', views.popular_locations, name='popular-locations'),
    path('', views.map_view, name='geo.index'),
]