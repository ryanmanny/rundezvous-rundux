import datetime

from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from django.utils import timezone
from django.contrib.gis import measure
from django.contrib.gis.db.models.functions import Distance

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
    gender = models.CharField(
        max_length=1,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
        ],
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
    location_updated_at = models.DateTimeField(
        auto_now_add=timezone.now,
        editable=True,
        null=True,
        blank=True,
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
        blank=True,
    )

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.display_name if self.display_name else 'NONE'} - {self.email}>"

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    def update_location(self, new_location):
        """
        Called by the middleware to update user's location
        """
        self.location = new_location
        self.location_updated_at = timezone.now()

        self.save()

        # TODO: Maybe this should only happen on log in
        # self.update_region()
        # if self.region is None:
        #     # User not in any supported region
        #     raise place_models.SupportedRegion.UnsupportedRegionError

        if self.active_rundezvous is not None:
            if self.is_near_rundezvous:
                self.handle_rundezvous_arrival()

    def update_region(self):
        """
        Called by the middleware to update user's region
        Uses User.location to automatically detect region
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
        """
        Returns True if user is within some distance of destination
        """
        if self.active_rundezvous is None:
            return

        distance = self.location.distance(
            self.active_rundezvous.landmark.location
        )
        # TODO: Figure out what units distance are in, it's probably meters

        return measure.Distance(m=distance) < const.MEETUP_DISTANCE_THRESHOLD

    def handle_rundezvous_arrival(self):
        """
        TODO: Make this an event or something like that?
        """
        raise NotImplementedError

    @property
    def new_users(self):
        """
        Gets all users within current region who user has not met with yet
        TODO: Exclude users who are not currently using the app
        or maybe add some flag that denotes looking for partner
        """
        return SiteUser.objects.filter(
            region=self.region,
        ).exclude(
            id=self.id,  # Has everyone met themselves?
        ).exclude(
            id__in=self.met_users.values_list('id', flat=True),
        )

    def get_new_users_within(self, miles):
        """
        Gets all users less than distance miles away from user
        """
        return self.new_users.filter(
            location__isnull=False,
        ).filter(
            location__distance_lte=(self.location, measure.D(mi=miles))
        )

    @property
    def closest_new_user(self):
        """
        Gets closest new user to user
        """
        return self.get_new_users_within(miles=2).annotate(
            # TODO: Find a way to do this without being repetitive
            distance=Distance('location', self.location)
        ).order_by(
            'distance'
        ).first()


class Preferences(models.Model):
    class Meta:
        verbose_name = 'preferences'
        verbose_name_plural = 'preferences'

    user = models.OneToOneField(
        SiteUser,
        primary_key=True,
        on_delete=models.CASCADE,
    )

    # GENDER PREFERENCES - Compared against User.gender
    males = models.BooleanField(default=False)
    females = models.BooleanField(default=False)
    others = models.BooleanField(default=False)

    # ACTIVITY PREFERENCES - Compared against other User.profiles
    hookups = models.BooleanField(default=False)
    # TODO: Add some less obvious ones


class Rundezvous(models.Model):
    """
    The titular unit of data, describes the meetup between two+ users
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
            MaxValueValidator(const.MAX_RUNDEZVOUS_EXPIRATION.seconds),
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
