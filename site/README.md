# Desktop Cat — download site

A small Django app that serves a single landing/download page for Desktop
Cat. No database, no accounts, no forms -- it fetches the latest stable
(`main`, tag `vX.Y.Z`) and staging (`staging`, tag `staging-latest`)
release info straight from the GitHub Releases API server-side, caches it
for 5 minutes, and renders download buttons for whatever assets each
release actually has (AppImage, Windows `.zip`, macOS `.zip`, Flatpak).

Asset filenames are matched against what `.github/workflows/release.yml`
and `.github/workflows/staging.yml` (in the repo root) actually upload --
if those change, update `downloads/github.py`'s `ASSET_MATCHERS` to match.

## Run it

From the repo root (`compose.yml` and `.env.example` live there, not in
this directory, so `docker compose` can build both this site and, later,
anything else in the repo from one place):

```sh
cp .env.example .env
# edit .env -- at minimum set DJANGO_SECRET_KEY and DJANGO_ALLOWED_HOSTS
docker compose up --build
```

Serves on `http://localhost:8000`. Put your own reverse proxy (nginx,
Caddy, Traefik, whatever you already run) in front of it for TLS/domain
routing -- this container only speaks plain HTTP.

## Local dev without Docker

From this directory (`site/`):

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DJANGO_DEBUG=true python manage.py runserver
```

## Notes

- `GITHUB_TOKEN` is optional -- only raises the API rate limit (60/hr ->
  5000/hr), not required at low traffic since responses are cached.
- The staging release won't exist until `staging.yml`'s `publish-staging`
  job actually runs against the current tag naming (`staging-latest`) --
  until then that tab shows a "not published yet" message instead of
  broken links.
- The cache is file-based (`DJANGO_CACHE_DIR`, defaults to
  `/tmp/desktopcat-site-cache`, mounted as a named volume in the root
  `compose.yml`) rather than in-memory, so it's shared across all
  gunicorn worker processes.
