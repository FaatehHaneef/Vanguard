from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recipes/", views.recipe_list, name="recipes"),
    path("recipes/<slug:slug>/", views.recipe_detail, name="recipe"),
    path("list/", views.home, name="shopping_list"),
    path("submit/", views.home, name="submit"),
    path("about/", views.home, name="about"),
]
