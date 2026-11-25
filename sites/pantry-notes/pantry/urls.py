from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("", include("recipes.urls")),
    # Static files are served by Django itself, so one process serves the whole site.
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_DIR}),
]
