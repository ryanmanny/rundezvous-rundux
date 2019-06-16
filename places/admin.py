from django.contrib.gis import admin

from places import models


@admin.register(models.Country)
class CountryAdmin(admin.GeoModelAdmin):
    class StateInline(admin.TabularInline):
        model = models.State

        extra = 0

    inlines = [StateInline]


@admin.register(models.Landmark)
class LandmarkAdmin(admin.GeoModelAdmin):
    pass
