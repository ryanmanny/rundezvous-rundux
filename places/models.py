from django.contrib.gis.db import models

from places import managers
from places import const


class SupportedRegion(models.Model):
    """
    Describes the geometry of a Region supported by the system
    This system may need to be totally changed in the future
    """
    objects = managers.SupportedRegionManager()

    name = models.CharField(max_length=50)

    region = models.PolygonField(srid=const.DEFAULT_SRID)
    projected_srid = models.IntegerField(
        # The SRID used to calculate distance between locations in this region
        default=const.DEFAULT_PROJECTION_SRID,
    )

    def __str__(self):
        return self.name


class Landmark(models.Model):
    """
    Describes a Landmark that users can meet at
    """
    objects = managers.LandmarkManager()

    name = models.CharField(max_length=50)
    # place_type = models.CharField(choices=)

    location = models.PointField(srid=const.DEFAULT_SRID)

    region = models.ForeignKey(
        SupportedRegion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name
