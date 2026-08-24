from django.conf import settings
from django.db import models

# Plain tuple, not models.TextChoices, to avoid a second class -- see
# Python/scripts/no_classes_check.py's models.py exemption.
STATUS_CHOICES = (
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("canceled", "Canceled"),
)


class Purchase(models.Model):
    """One-time download purchase. One row per user -- no renewal/period
    fields, since this is a single payment that unlocks downloads forever,
    not a subscription."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchase")
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} ({self.status})"
