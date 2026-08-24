from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from .models import Purchase

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    purchase, _ = Purchase.objects.get_or_create(user=request.user)
    if purchase.status == "paid":
        return redirect("index")
    return render(request, "purchases/checkout.html", {"purchase": purchase, "next_url": _safe_next(request, "next")})


def _safe_next(request, param):
    next_url = request.POST.get(param) or request.GET.get(param) or ""
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return next_url
    return ""


@login_required
@require_POST
def start_checkout(request):
    purchase, _ = Purchase.objects.get_or_create(user=request.user)
    success_url = request.build_absolute_uri(reverse("purchases:checkout_success"))
    next_url = _safe_next(request, "next")
    if next_url:
        success_url = f"{success_url}?next={next_url}"
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        customer_email=request.user.email or None,
        client_reference_id=str(request.user.pk),
        success_url=success_url,
        cancel_url=request.build_absolute_uri(reverse("purchases:checkout_cancel")),
    )
    purchase.stripe_checkout_session_id = session.id
    purchase.save(update_fields=["stripe_checkout_session_id"])
    return redirect(session.url, permanent=False)


@login_required
def checkout_success(request):
    next_url = _safe_next(request, "next")
    return render(request, "purchases/success.html", {"next_url": next_url})


@login_required
def checkout_cancel(request):
    return render(request, "purchases/cancel.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    # No Django session/CSRF cookie on Stripe's server-to-server POST, so
    # @csrf_exempt is required here -- the Stripe signature check below is
    # the real security control for this endpoint, not CSRF.
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponseBadRequest("invalid payload or signature")

    if event["type"] == "checkout.session.completed":
        # .to_dict() -- StripeObject isn't a dict and doesn't support .get().
        session = event["data"]["object"].to_dict()
        user_id = session.get("client_reference_id")
        if user_id:
            updated = Purchase.objects.filter(user_id=user_id).update(
                status="paid",
                paid_at=timezone.now(),
                stripe_customer_id=session.get("customer") or "",
                stripe_payment_intent_id=session.get("payment_intent") or "",
            )
            if not updated:
                Purchase.objects.create(
                    user_id=user_id,
                    status="paid",
                    paid_at=timezone.now(),
                    stripe_checkout_session_id=session.get("id") or "",
                    stripe_customer_id=session.get("customer") or "",
                    stripe_payment_intent_id=session.get("payment_intent") or "",
                )

    return HttpResponse(status=200)
