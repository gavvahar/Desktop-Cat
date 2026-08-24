"""Download page for Desktop Cat, gated behind login: free via Authentik
SSO, or a one-time Stripe purchase for standalone accounts. Landing page
content itself stays public -- only the download links require auth.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key-set-DJANGO_SECRET_KEY-in-prod")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.openid_connect",
    "downloads",
    "purchases",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Must come after AuthenticationMiddleware -- it reads request.user.
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ROOT_URLCONF = "desktopcat_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "desktopcat_site.wsgi.application"

# SQLite on a persistent volume -- fits this project's single-container,
# no-Postgres-service deployment better than standing up a separate DB
# service. Parent dir is created here since the sqlite backend won't do it
# for us (matters for local `runserver` dev; the Docker volume mount point
# already exists by the time the container starts).
DJANGO_DB_PATH = Path(os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "data" / "db.sqlite3")))
DJANGO_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DJANGO_DB_PATH,
    }
}

# File-based (not in-memory) so the cache is shared across gunicorn worker
# processes -- otherwise every worker would hit the GitHub API separately.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.environ.get("DJANGO_CACHE_DIR", "/tmp/desktopcat-site-cache"),
    },
    # Separate from "default" so frequent session writes can't evict the
    # small, high-value GitHub release cache entries (FileBasedCache
    # defaults to MAX_ENTRIES=300 with random culling past that), and so a
    # burst of traffic to the release cache can't evict active sessions.
    "sessions": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.environ.get("DJANGO_SESSION_CACHE_DIR", "/tmp/desktopcat-site-session-cache"),
        "OPTIONS": {"MAX_ENTRIES": 10000},
    },
}

# Cache-backed rather than the DB-backed default: gunicorn runs multiple
# worker processes sharing one SQLite file, and a session write on every
# request would be a real write-lock contention risk there.
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"

# Mandatory email verification (see allauth ACCOUNT_EMAIL_VERIFICATION)
# needs real outbound email. Falls back to the console backend -- which
# prints the email to stdout instead of sending it -- whenever EMAIL_HOST
# isn't set, so signup works in local dev without real SMTP creds.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend" if os.environ.get("EMAIL_HOST") else "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@desktopcat.local")

# django-allauth: standalone accounts require a verified email before login
# works (needs the EMAIL_BACKEND configured above); logout stays a
# confirm-page/POST action rather than one-click GET, consistent with CSRF
# protection now being enabled.
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_LOGOUT_ON_GET = False
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "index"

# Authentik SSO via OIDC. provider_id="authentik" is what ends up in
# SocialAccount.provider for users who sign in this way -- that's how
# downloads.views.download_asset tells an SSO login apart from a
# standalone (paying) account.
SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "authentik",
                "name": "Authentik",
                "client_id": os.environ.get("AUTHENTIK_OIDC_CLIENT_ID", ""),
                "secret": os.environ.get("AUTHENTIK_OIDC_CLIENT_SECRET", ""),
                "settings": {
                    "server_url": os.environ.get("AUTHENTIK_OIDC_ISSUER", ""),
                },
            }
        ]
    }
}

# Stripe one-time purchase for standalone (non-SSO) accounts. STRIPE_PRICE_ID
# is a Price created once in the Stripe Dashboard, not built from a raw
# amount here, so the price can change without a code deploy.
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Respect X-Forwarded-Proto from whatever reverse proxy terminates TLS in
# front of this container.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
