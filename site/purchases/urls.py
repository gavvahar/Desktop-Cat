from django.urls import path

from . import views

app_name = "purchases"

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("start/", views.start_checkout, name="start_checkout"),
    path("success/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
]
