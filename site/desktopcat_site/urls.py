from django.urls import include, path

urlpatterns = [
    path("", include("downloads.urls")),
]
