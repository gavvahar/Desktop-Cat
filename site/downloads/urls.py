from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dl/<str:channel>/<str:platform_key>/", views.download_asset, name="download_asset"),
]
