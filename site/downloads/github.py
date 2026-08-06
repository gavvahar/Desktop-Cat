"""Release data comes straight from the GitHub Releases API, cached for a
few minutes -- no database, no sync job, one source of truth (GitHub
itself). See .github/workflows/release.yml (tags vX.Y.Z on `main`) and
staging.yml (rolling `staging-latest` tag on `staging`) in the main repo
for how those releases get published; asset filenames here must match
what those workflows actually upload.
"""

import os, requests

from django.core.cache import cache
from django.utils.dateparse import parse_datetime

GITHUB_REPO = os.environ.get("GITHUB_REPO", "gavvahar/Desktop-Cat")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
CACHE_TTL_SECONDS = 300
REQUEST_TIMEOUT = 5

# (key, display label, filename matcher) -- order here is display order.
ASSET_MATCHERS = [
    ("linux", "Linux (AppImage)", lambda name: name.endswith(".AppImage")),
    ("windows", "Windows", lambda name: name.endswith("windows.zip")),
    ("macos", "macOS", lambda name: name.endswith("macos.zip")),
    ("flatpak", "Flatpak", lambda name: name.endswith(".flatpak")),
]

_MISS = object()  # distinguishes "not cached" from "cached, and the value is None"


def _headers():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def _fetch(url):
    try:
        resp = requests.get(url, headers=_headers(), timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    return resp.json()


def _release_info(release):
    if not release:
        return None
    assets = release.get("assets", [])
    platforms = []
    for key, label, matches in ASSET_MATCHERS:
        asset = next((a for a in assets if matches(a["name"])), None)
        if asset:
            platforms.append(
                {
                    "key": key,
                    "label": label,
                    "name": asset["name"],
                    "url": asset["browser_download_url"],
                    "size_mb": round(asset["size"] / (1024 * 1024), 1),
                }
            )
    return {
        "tag": release.get("tag_name"),
        # GitHub returns an ISO8601 string -- Django's |date template
        # filter needs an actual datetime to format it, not a string.
        "published_at": parse_datetime(release["published_at"]) if release.get("published_at") else None,
        "html_url": release.get("html_url"),
        "platforms": platforms,
    }


def _cached(cache_key, url):
    cached = cache.get(cache_key, _MISS)
    if cached is not _MISS:
        return cached
    info = _release_info(_fetch(url))
    cache.set(cache_key, info, CACHE_TTL_SECONDS)
    return info


def get_prod_release():
    return _cached("gh_release_prod", f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest")


def get_staging_release():
    return _cached("gh_release_staging", f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/staging-latest")
