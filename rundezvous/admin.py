"""
Defines sensible admin panel for Rundezvous app
"""

from django.contrib.gis import admin

from rundezvous import models


class PreferencesInline(admin.TabularInline):
    model = models.Preferences

    fieldsets = [
        ('Gender', {
            'fields': (
                'males',
                'females',
                'others',
            ),
        }),
        ('Activities', {
            'fields': (
                'hookups',
            ),
        }),
    ]


class MetUsersInline(admin.TabularInline):
    model = models.Review
    fk_name = 'reviewer'

    extra = 0


@admin.register(models.SiteUser)
class SiteUserAdmin(admin.GeoModelAdmin):  # TODO: Change to OSMModelAdmin?
    """
    SiteUser Admin page
    Organizes fields into three sections based on logical partitions of a user
    """
    model = models.SiteUser

    # These fields must be specified here to use them in fieldsets
    readonly_fields = (
        'location_updated_at',
        'latitude',
        'longitude',
        'active_rundezvous',  # Add a link?
    )

    fieldsets = [
        ('User', {
            'fields': (
                'username',
                'email',
                'is_superuser',
                'is_staff',
                'is_active',
            ),
        }),
        ('Profile', {
            'fields': (
                'display_name',
                'gender',
                'reputation',
            ),
        }),
        ('Location', {
            'fields': (
                'location',
                'latitude',
                'longitude',
                'region',
                'location_updated_at',
            ),
        }),
        ('Rundezvous', {
           'fields': (
               'active_rundezvous',
           ),
        }),
    ]

    inlines = (PreferencesInline, MetUsersInline)


@admin.register(models.Rundezvous)
class RundezvousAdmin(admin.ModelAdmin):
    pass
