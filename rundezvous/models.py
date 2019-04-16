import datetime

from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from django.utils import timezone
from django.contrib.gis import measure

from django.core.validators import MinValueValidator, MaxValueValidator

# Rundezvous depends on Chat, Places apps
from chat import models as chat_models
from places import models as place_models

from rundezvous import const
from rundezvous import managers


class SiteUser(auth_models.AbstractUser):
    email = models.EmailField(  # Overrides email field of AbstractUser
        unique=True,
        null=False,
        blank=False,
    )

    # PROFILE DATA
    display_name = models.CharField(
        max_length=1,  # Identify users by single Unicode char INNOVATION
        null=True,
        blank=True,
    )
    # display_color TODO: Import django-colorpicker
    reputation = models.IntegerField(
        default=0,
    )

    # LOCATION DATA
    location = models.PointField(  # For position-based game elements
        verbose_name="Last Known Location",
        null=True,
        blank=True,
    )
    region = models.ForeignKey(
        place_models.SupportedRegion,
        verbose_name="Last Known Region",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # RUNDEZVOUS DATA
    active_room = models.ForeignKey(  # User can only access one room at a time
        chat_models.ChatRoom,
        null=True,  # User can exist without room
        blank=True,
        on_delete=models.SET_NULL,
    )
    active_rundezvous = models.ForeignKey(
        'Rundezvous',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # User can exist without Rundezvous
    )
    met_users = models.ManyToManyField(
        'self',
        symmetrical=True,  # If I've met you, you've met me
    )

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.display_name if self.display_name else 'NONE'} - {self.email}>"

    def update_location(self, new_location):
        """Called by the middleware to update user's location
        """
        self.location = new_location

        # TODO: Maybe this should only happen on log in
        self.update_region()
        if self.region is None:
            # User not in any supported region
            raise place_models.SupportedRegion.UnsupportedRegionError

        if self.is_near_rundezvous:
            self.handle_rundezvous_arrival()

    def update_region(self):
        """Returns whether user is in a supported location
        """
        try:
            region = place_models.SupportedRegion.objects.get(
                region__intersects=self.location,
            )
        except place_models.SupportedRegion.DoesNotExist:
            self.region = None
        except place_models.SupportedRegion.MultipleObjectsReturned:
            # TODO: Consider overlapping regions, maybe log collisions here
            raise NotImplementedError
        else:
            self.region = region

        self.save()

    @property
    def is_near_rundezvous(self):
        """Returns True if user is within some distance of destination
        """
        distance = self.location.distance(
            self.active_rundezvous.landmark.location)

        return measure.Distance(m=distance) < const.meetup_distance_threshold

    def handle_rundezvous_arrival(self):
        """TODO: Make this an event or something like that?
        """
        raise NotImplementedError

    def new_users(self):
        """Gets users within current region who user has not met with yet
        """
        return SiteUser.objects.filter(
            region=self.region,
        ).exclude(
            id=self,
            id__not_in=self.met_users,  # Has everyone met themselves?
        )

    def new_users_within(self, miles):
        """Gets all users within distance miles of user
        """
        distance = measure.Distance(mi=miles)

        return self.new_users().distance(self.location).filter(
            location__distance_lt=(self.location, distance),
        )  # Annotates QuerySet with distance

    def closest_new_user(self):
        return self.new_users_within(miles=2).first('distance')


class Rundezvous(models.Model):
    """The titular unit of data, describes the meetup between two+ users
    """
    objects = managers.RundezvousManager.\
        from_queryset(managers.RundezvousSet)
    unexpired = managers.RundezvousUnexpiredManager.\
        from_queryset(managers.RundezvousSet)

    created_at = models.DateTimeField(  # Used to time out users
        auto_now_add=True,
    )
    landmark = models.ForeignKey(
        place_models.Landmark,
        on_delete=models.CASCADE,  # Meetup needs a location
    )
    expiration_seconds = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(const.max_rundezvous_expiration.seconds),
        ]
    )

    @property
    def time_elapsed(self) -> datetime.timedelta:
        return timezone.now() - self.created_at

    @property
    def time_left(self) -> datetime.timedelta:
        return datetime.timedelta(
            seconds=self.expiration_seconds - self.time_elapsed.seconds,
        )

    @property
    def is_expired(self):
        return self.time_left < datetime.timedelta(seconds=0)
