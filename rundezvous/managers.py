from django.contrib.gis.db import models
from django.contrib.gis.db.models import F

from django.contrib.gis.geos import Point
# https://docs.djangoproject.com/en/2.1/ref/contrib/gis/functions
from django.contrib.gis.db.models.functions import Centroid
# https://docs.djangoproject.com/en/2.1/ref/contrib/gis/geoquerysets
from django.contrib.gis.db.models.aggregates import Collect

from django.utils import timezone

from rundezvous import const


# SiteUser
class SiteUserSet(models.QuerySet):
    def add_close_users(self):
        """I think this will have to be a crummy approximation for now
        """
        ...

    def get_midpoint(self) -> Point:
        """
        Finds midpoint from User.location
        """
        return self.aggregate(
            midpoint=Centroid(  # Centroid calculates the midpoint of a Geometry
                Collect('location')
            )
        )['midpoint']


class SiteUserManager(models.Manager):
    pass


# Rundezvous
class RundezvousSet(models.QuerySet):
    def add_time_left(self):
        """Annotates time left in seconds on Query
        Excludes expired results
        """
        now = timezone.now()
        return self.filter(
            created_at__gt=now - const.MAX_RUNDEZVOUS_EXPIRATION
        ).annotate(
            time_left=now - F('created_at') - F('expiration_seconds')
        ).filter(
            time_left__gt=0
        )


class RundezvousManager(models.Manager):
    pass


class RundezvousUnexpiredManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().add_time_left()
