from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recipes/", views.recipe_list, name="recipes"),
    path("recipes/<slug:slug>/", views.recipe_detail, name="recipe"),
    path("list/", views.shopping_list, name="shopping_list"),
    path("list/add/<slug:slug>/", views.list_add, name="list_add"),
    path("list/remove/<slug:slug>/", views.list_remove, name="list_remove"),
    path("list/clear/", views.list_clear, name="list_clear"),
    path("submit/", views.submit, name="submit"),
    path("submit/thanks/<int:number>/", views.submitted, name="submitted"),
    path("about/", views.home, name="about"),
]
