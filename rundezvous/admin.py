"""
Defines sensible admin panel for Rundezvous app
"""

from django.contrib.gis import admin

from rundezvous import models


@admin.register(models.SiteUser)
class SiteUserAdmin(admin.GeoModelAdmin):
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

    inlines = (PreferencesInline, MetUsersInline)


@admin.register(models.Rundezvous)
class RundezvousAdmin(admin.ModelAdmin):
    readonly_fields = ('started_at',)
    fields = ('started_at', 'ended_at', 'landmark', 'expiration_seconds',)

    class UserInline(admin.TabularInline):
        model = models.SiteUser.rundezvouses.through
        extra = 0

        show_change_link = True

    class ChatMessageInline(admin.TabularInline):
        model = models.ChatMessage

        extra = 1

    inlines = [UserInline, ChatMessageInline]
