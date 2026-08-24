from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("purchases/", include("purchases.urls")),
    path("", include("downloads.urls")),
]
