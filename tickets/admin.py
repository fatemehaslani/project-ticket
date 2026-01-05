from django.contrib import admin

from tickets.models import *

# Register your models here.

admin.site.register(SearchLog)
admin.site.register(Ticket)
admin.site.register(Category)
admin.site.register(Tag)