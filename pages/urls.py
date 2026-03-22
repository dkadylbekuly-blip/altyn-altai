from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("tours/", views.tours, name="tours"),
    path("collection/", views.collection, name="collection"),
    path("collection/<slug:slug>/", views.mineral_detail, name="mineral_detail"),
    path("collection-autocomplete/", views.mineral_autocomplete, name="mineral_autocomplete"),
    path("map/", views.map_view, name="map"),
    path("statistics/", views.statistics_view, name="statistics"),
    path("gallery/", views.gallery, name="gallery"),
    path("history/", views.history, name="history"),
]
