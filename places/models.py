from django.contrib.gis.db import models


class SupportedRegion(models.Model):
    """
    Describes the geometry of a Region supported by the system
    This may need to be totally changed in the future
    """
    name = models.CharField(max_length=50)

    region = models.PolygonField()  # Assume university is contiguous

    class UnsupportedRegionError(Exception):
        """User is not in any supported region
        """


class Landmark(models.Model):
    """
    Describes a Landmark that users can meet at
    """
    name = models.CharField(max_length=50)
    # place_type = models.CharField(choices=)

    location = models.PointField()

    region = models.ForeignKey(
        SupportedRegion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
