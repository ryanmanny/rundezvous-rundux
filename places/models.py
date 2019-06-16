from django.contrib.gis.db import models

from places import managers
from places import const


class Country(models.Model):
    class Meta:
        verbose_name_plural = 'countries'

    objects = managers.CountryManager()

    name = models.CharField(max_length=50, unique=True)

    region = models.MultiPolygonField(srid=const.DEFAULT_SRID)

    # The SRID used to calculate distance between locations in this region
    projection_srid = models.IntegerField(default=const.DEFAULT_PROJECTION_SRID)

    def __str__(self):
        return self.name


class State(models.Model):
    class Meta:
        unique_together = ('country', 'name')

    objects = managers.StateManager()

    country = models.ForeignKey(
        Country,
        related_name='states',
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=50)

    region = models.MultiPolygonField(srid=const.DEFAULT_SRID)

    # The SRID used to calculate distance between locations in this region
    # Falls back on the one used by Country if not defined
    _projection_srid = models.IntegerField(
        db_column='projection_srid',
        null=True,
        blank=True,
        default=None,
    )

    @property
    def projection_srid(self):
        if self._projection_srid is None:
            return self.country.projection_srid
        else:
            return self._projection_srid

    def __str__(self):
        return f"{self.name} ({self.country})"


class Landmark(models.Model):
    """A Landmark that users can meet at"""
    objects = managers.LandmarkManager()

    name = models.CharField(max_length=50)
    # place_type = models.CharField(choices=)

    location = models.PointField(srid=const.DEFAULT_SRID)

    state = models.ForeignKey(
        State,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name
