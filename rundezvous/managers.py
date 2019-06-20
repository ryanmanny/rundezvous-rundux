from django.contrib.gis.db import models
from django.contrib.auth import models as auth_models

from django.contrib.gis import measure

from django.contrib.gis.geos import Point
# https://docs.djangoproject.com/en/2.1/ref/contrib/gis/functions
from django.contrib.gis.db.models.functions import Distance, Centroid
# https://docs.djangoproject.com/en/2.1/ref/contrib/gis/geoquerysets
from django.contrib.gis.db.models.aggregates import Collect

from django.utils import timezone

from rundezvous import const


# SiteUser
class SiteUserSet(models.QuerySet):
    def get_midpoint(self) -> Point:
        """
        Aggregates midpoint from all User.locations
        """
        return self.aggregate(
            midpoint=Centroid(  # Centroid calculates the midpoint of a Geometry
                Collect('location')
            )
        )['midpoint']

    def filter_by_active(self):
        """Filters out users who haven't updated their location lately"""
        user_active_time = timezone.now() - const.USER_ACTIVE_TIME

        return self.filter(location_updated_at__gte=user_active_time)

    def order_by_closest_to(self, user):
        """
        Gets closest compatible user to current user
        """
        return self \
            .annotate(distance=Distance('location', user.location)) \
            .order_by('distance')


class SiteUserManager(auth_models.UserManager.from_queryset(SiteUserSet)):
    pass


# Rundezvous
class RundezvousSet(models.QuerySet):
    def add_expires_at(self):
        """
        Annotates QuerySet with expires_at datetime by using created_at and
        TODO: Stop supporting Spatialite so I can use this
        """
        raise NotImplementedError

        # return self.annotate(
        #     expires_at=ExpressionWrapper(
        #         F('created_at') + F('expiration_seconds') * timezone.timedelta(seconds=1),
        #         output_field=DateTimeField(),
        #     )
        # )


class RundezvousManager(models.Manager.from_queryset(RundezvousSet)):
    def expired(self):
        raise NotImplementedError

    def unexpired(self):
        raise NotImplementedError
