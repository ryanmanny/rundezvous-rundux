from django.contrib import admin

from places import models


@admin.register(models.SupportedRegion)
class SupportedRegionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    pass
