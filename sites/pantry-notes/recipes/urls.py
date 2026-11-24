from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recipes/", views.home, name="recipes"),
    path("list/", views.home, name="shopping_list"),
    path("submit/", views.home, name="submit"),
    path("about/", views.home, name="about"),
]
