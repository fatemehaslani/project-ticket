from .services import SiteService

def site_settings(request):
    return {
        "site_settings": SiteService.settings()
    }