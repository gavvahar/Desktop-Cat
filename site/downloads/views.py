from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from allauth.socialaccount.models import SocialAccount

from purchases.models import Purchase

from . import github


def index(request):
    context = {
        "prod": github.get_prod_release(),
        "staging": github.get_staging_release(),
        "repo_url": f"https://github.com/{github.GITHUB_REPO}",
    }
    return render(request, "downloads/index.html", context)


@login_required
def download_asset(request, channel, platform_key):
    """Proxies the actual click-through to GitHub's asset-by-ID endpoint
    (see github.resolve_asset_download_url) instead of linking straight to
    browser_download_url, so downloads keep working whether or not the
    repo is public.

    Gated: free for anyone who signed in via Authentik SSO (a SocialAccount
    with provider="authentik" -- see SOCIALACCOUNT_PROVIDERS' provider_id),
    otherwise requires a paid Purchase (standalone accounts)."""
    is_sso = SocialAccount.objects.filter(user=request.user, provider="authentik").exists()
    if not is_sso and not Purchase.objects.filter(user=request.user, status="paid").exists():
        return redirect(f"{reverse('purchases:checkout')}?next={request.path}")

    release = github.get_prod_release() if channel == "prod" else github.get_staging_release() if channel == "staging" else None
    if not release:
        raise Http404("Release not found")
    asset = next((p for p in release["platforms"] if p["key"] == platform_key), None)
    if not asset:
        raise Http404("No matching download for that platform")
    redirect_url = github.resolve_asset_download_url(asset["id"])
    if not redirect_url:
        raise Http404("Could not resolve a download link from GitHub right now")
    return HttpResponseRedirect(redirect_url)
