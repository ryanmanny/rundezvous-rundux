"""
Defines sensible admin panel for Rundezvous app
"""

from django.contrib import admin

from rundezvous import models


@admin.register(models.SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    model = models.SiteUser

    fields = [  # Hides fields that I don't care about
        'username',
        'email',

        'is_superuser',
        'is_staff',
        'is_active',

        'display_name',
        'reputation',
        'active_room',
        'last_location',
    ]
