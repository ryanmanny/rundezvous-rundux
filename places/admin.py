from django.contrib.gis import admin

from places import models


@admin.register(models.SupportedRegion)
class SupportedRegionAdmin(admin.GeoModelAdmin):
    pass


@admin.register(models.Landmark)
class LandmarkAdmin(admin.GeoModelAdmin):
    pass
