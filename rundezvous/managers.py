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
        """
        Filters out users who haven't updated their location lately
        """
        user_active_time = timezone.now() - const.USER_ACTIVE_TIME

        return self.filter(location_updated_at__gte=user_active_time)

    def havent_met(self, user):
        """
        Gets all users within current region who user has not met with yet
        """
        met_users = user.met_users.values_list('id', flat=True)

        return self.filter(
            country=user.country,
        ).exclude(
            id=user.id,  # Has everyone met themselves?
        ).exclude(  # CHAIN, don't combine
            id__in=Subquery(met_users),
        )

    def meetable_users_within(self, user, distance: measure.Distance):
        """
        Gets all users less than distance miles away from user
        This should be used to find the next user to match with
        TODO: Generalize the distance stuff into its own Query method
        """
        from rundezvous.models import SiteUser

        return self.active().havent_met(user).filter(
            location__distance_lte=(user.location, distance),
            status=SiteUser.Status.LOOKING,
        )

    def order_by_closest_to(self, user):
        """
        Gets closest compatible user to current user
        """
        return self \
            .annotate(distance=Distance('location', user.location)) \
            .order_by('distance')


class SiteUserManager(auth_models.UserManager.from_queryset(SiteUserSet)):
    def active(self):
        return self.get_queryset().active()


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
