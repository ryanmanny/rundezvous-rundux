from django.contrib.gis.db import models
from django.contrib.auth import models as auth_models
from django.contrib.gis.db.models import F, Subquery

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

    def active(self):
        user_active_time = timezone.now() - const.USER_ACTIVE_TIME

        return self.filter(location_updated_at__gte=user_active_time)

    def havent_met(self, user):
        """
        Gets all users within current region who user has not met with yet
        """
        met_users = user.met_users.values_list('id', flat=True)  # Symmetrical

        return self.filter(
            region=user.region,
        ).exclude(
            id=user.id,  # Has everyone met themselves?
        ).exclude(  # CHAIN, don't combine
            id__in=Subquery(met_users),
        )

    def order_by_closest_to(self, user):
        """
        Gets closest compatible user to current user
        """
        return self.annotate(
            distance=Distance('location', user.location),
        ).order_by(
            'distance',
        )

    def meetable_users_within(self, user, miles):
        """
        Gets all users less than distance miles away from user
        """
        from rundezvous.models import SiteUser

        return self.active().havent_met(
            user,
        ).filter(
            location__distance_lte=(user.location, measure.D(mi=miles)),
            rundezvous_status=SiteUser.LOOKING,
        ).order_by_closest_to(
            user,
        )


class SiteUserManager(auth_models.UserManager.from_queryset(SiteUserSet)):
    def active(self):
        return self.get_queryset().active()


# Rundezvous
class RundezvousSet(models.QuerySet):
    def add_time_left(self):
        """
        Annotates time left in seconds on Query
        """
        now = timezone.now()
        return self.filter(
            created_at__gt=now - const.MAX_RUNDEZVOUS_EXPIRATION,
        ).annotate(
            time_left=now - F('created_at') - F('expiration_seconds'),
        )

    def expired(self):
        return self.filter(
            time_left__gt=0,
        )

    def unexpired(self):
        return self.filter(
            time_left__lte=0,
        )


class RundezvousManager(models.Manager.from_queryset(RundezvousSet)):
    def expired(self):
        return self.get_queryset().expired()

    def unexpired(self):
        return self.get_queryset().unexpired()
