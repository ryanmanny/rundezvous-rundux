import datetime

from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from django.contrib.gis.db.models import Subquery

from django.utils import timezone
from django.contrib.gis import measure

from django.core.validators import MinValueValidator, MaxValueValidator

# Rundezvous depends on Chat, Places apps
from chat import models as chat_models
from places import models as place_models

from rundezvous import const
from rundezvous import managers


class SiteUser(auth_models.AbstractUser):
    objects = managers.SiteUserManager.from_queryset(managers.SiteUserSet)()

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
        db_index=True,  # To get active users quickly
    )

    # RUNDEZVOUS DATA
    NONE = 'N'
    LOOKING = 'L'
    RUNNING = 'R'
    REVIEW = 'V'

    rundezvous_status = models.CharField(
        max_length=1,
        choices=[
            (NONE, 'None'),
            (LOOKING, 'Looking'),
            (RUNNING, 'Running'),
            (REVIEW, 'Review'),
        ]
    )
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

        if self.check_rundezvous_arrived():
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

    def check_rundezvous_arrived(self):
        """
        Returns True if User made it to Rundezvous destination
        """
        if self.active_rundezvous is None:
            return None

        rundezvous_location = self.active_rundezvous.landmark.location
        distance = self.location.distance(rundezvous_location)
        # TODO: Figure out what units distance are in, it's probably meters

        return measure.D(m=distance) < const.MEETUP_DISTANCE_THRESHOLD

    def handle_rundezvous_arrival(self):
        """
        Should be used as a callback on location update
        """
        self.rundezvous_status = self.REVIEW
        self.save()

        active_rundezvous = self.active_rundezvous

        # This will get overwritten if the next person made it
        active_rundezvous.ended_at = timezone.now()
        active_rundezvous.save()


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


class Review(models.Model):
    """
    A review must be written for the other user after every Rundezvous
    """
    reviewer = models.ForeignKey(
        SiteUser,
        related_name='reviews',
        on_delete=models.CASCADE,
    )
    reviewed = models.ForeignKey(
        SiteUser,
        related_name='reviews_for',
        on_delete=models.CASCADE,
    )

    showed_up = models.BooleanField(
        null=True,
        blank=True,
        default=None,
    )



class RundezvousLog(models.Model):
    """
    Logs what happened on a completed Rundezvous
    """
    SUCCESSFUL = 'S'
    FAILED = 'F'
    EXPIRED = 'E'

    status = models.CharField(
        max_length=1,
        choices=[
            (SUCCESSFUL, 'Successful'),
            (FAILED, 'Failed'),
            (EXPIRED, 'Expired'),
        ],
    )

    started = models.DateTimeField()
    ended = models.DateTimeField(
        null=True,  # Null when the Rundezvous expired
        blank=True,
    )

    chatroom = models.ForeignKey(
        chat_models.ChatRoom,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )


class Rundezvous(models.Model):
    """
    The titular unit of data, describes the meetup between two+ users
    """
    class Meta:
        verbose_name = 'rundezvous'
        verbose_name_plural = 'rundezvouses'  # (nonstandard, rare)

    objects = managers.RundezvousManager.from_queryset(managers.RundezvousSet)()

    created_at = models.DateTimeField(  # Used to time out users
        auto_now_add=True,
    )
    ended_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
    )

    chatroom = models.ForeignKey(
        chat_models.ChatRoom,
        on_delete=models.CASCADE,  # This missing would be messy
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

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.siteuser_set} meeting at {self.landmark}>"

    @property
    def time_elapsed(self) -> datetime.timedelta:
        return timezone.now() - self.created_at

    @property
    def time_left(self) -> datetime.timedelta:
        return datetime.timedelta(
            seconds=self.expiration_seconds - self.time_elapsed.seconds,
        )

    @property
    def expiration_datetime(self) -> datetime.datetime:
        return self.created_at + datetime.timedelta(
            seconds=self.expiration_seconds,
        )

    @property
    def is_expired(self):
        return self.time_left < datetime.timedelta(seconds=0)

    def clean_up(self, status=RundezvousLog.EXPIRED):
        """
        The function is called when a Rundezvous is finished
        """
        users = self.siteuser_set.all()

        RundezvousLog.objects.create(
            status=status,
            started=self.created_at,
            stopped=self.ended_at or self.expiration_datetime,
            users=Subquery(users),
            chat_room=users.first().active_room,  # Assume it was the same
        )

        self.delete()
