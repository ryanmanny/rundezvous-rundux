from django.contrib.gis.db import models

from django.contrib.gis.db.models.functions import Distance


class LandmarkSet(models.QuerySet):
    def order_by_closest_to(self, point):
        return self \
            .annotate(distance=Distance('location', point)) \
            .order_by('distance')


class LandmarkManager(models.Manager.from_queryset(LandmarkSet)):
    pass
