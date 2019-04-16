"""
Defines sensible admin panel for Rundezvous app
"""

from django.contrib import admin

from rundezvous import models


@admin.register(models.SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    """
    SiteUser Admin page
    Organizes fields into three sections based on logical partitions of a user
    """
    model = models.SiteUser

    fieldsets = [
        ('User', {
            'fields': ('username', 'email', 'is_superuser', 'is_staff', 'is_active',),
        }),
        ('Profile', {
            'fields': ('display_name', 'active_room', 'reputation',),
        }),
        ('Location', {
            'fields': ('location', 'region',),
        }),
    ]
