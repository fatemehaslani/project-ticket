from django.contrib import admin
from .models import SiteSetting

# Register your models here.

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()
