from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):


    list_display = ("id", "name", "email_id", "phone")
    list_filter = ("id", "name")

admin.site.register(Contact, ContactAdmin)

