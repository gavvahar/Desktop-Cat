from django.shortcuts import render

from . import github


def index(request):
    context = {
        "prod": github.get_prod_release(),
        "staging": github.get_staging_release(),
        "repo_url": f"https://github.com/{github.GITHUB_REPO}",
    }
    return render(request, "downloads/index.html", context)
