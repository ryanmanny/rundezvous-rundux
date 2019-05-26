from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from django.utils import timezone
from django.contrib.gis import measure

from django.core.validators import MinValueValidator, MaxValueValidator

# Rundezvous depends on Chat, Places apps
from places import models as place_models

from rundezvous import const
from rundezvous import managers


class SiteUser(auth_models.AbstractUser):
    objects = managers.SiteUserManager()

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
    class Status:
        NONE = 'N'
        LOOKING = 'L'
        RUNNING = 'R'
        REVIEW = 'V'

    status = models.CharField(
        # This field is used to filter users based on what they're doing
        # TODO: Formalize this into the State Pattern?
        max_length=1,
        choices=[
            (Status.NONE, 'None'),
            (Status.LOOKING, 'Looking'),
            (Status.RUNNING, 'Running'),
            (Status.REVIEW, 'Review'),
        ],
        default=Status.NONE,
    )
    rundezvouses = models.ManyToManyField(
        'Rundezvous',
        related_name='users',
        through='UserToRundezvous',
        blank=True,
    )
    met_users = models.ManyToManyField(
        'self',
        through='Review',
        symmetrical=False,
        blank=True,
    )

    def __str__(self):
        return f"{self.display_name or 'NONE'} - {self.email}"

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    @property
    def active_rundezvous(self):
        try:
            return self.usertorundezvous_set.objects.get(
                is_active=True,
            )
        except Rundezvous.DoesNotExist:
            return None
        except Rundezvous.MultipleObjectsReturned:
            # TODO: Figure out what to do here, this is bad but possible
            raise

    def update_location(self, new_location):
        """
        Called by the middleware to update user's location
        """
        self.location = new_location
        self.location_updated_at = timezone.now()

        self.save()

        # TODO: Maybe this should only happen on log in, could get slow
        # self.update_region()
        # if self.region is None:
        #     # User not in any supported region
        #     raise place_models.SupportedRegion.UnsupportedRegionError

        if self.check_rundezvous_arrived():
            self.handle_rundezvous_arrival()

    def update_region(self):
        """
        Uses User.location to update user's region
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
        # TODO: Figure out what the distance function returns

        return distance < const.MEETUP_DISTANCE_THRESHOLD

    def handle_rundezvous_arrival(self):
        """
        Should be used as a callback on location update
        """
        self.status = self.Status.REVIEW
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
        null=True,  # Null if they're not sure
        blank=True,
        default=None,
    )

    # TODO: Add more criteria, but be careful not to get too judgmental
    # Maybe like describe in one word or a multiple choice 'aura' field


class Rundezvous(models.Model):
    """
    The titular unit of data, describes the meetup between two+ users
    """
    class Meta:
        verbose_name = 'rundezvous'
        verbose_name_plural = 'rundezvouses'  # (nonstandard, rare)

    objects = managers.RundezvousManager()

    started_at = models.DateTimeField(  # Used to time out users
        auto_now_add=True,
    )
    ended_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
    )

    landmark = models.ForeignKey(
        place_models.Landmark,
        on_delete=models.CASCADE,  # Meetup needs a location
    )
    expiration_seconds = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(const.MAX_RUNDEZVOUS_EXPIRATION.seconds),
        ],
    )

    def __str__(self):
        return f"{self.users} meeting at {self.landmark}"

    @property
    def expires_at(self) -> timezone.datetime:
        return self.started_at + timezone.timedelta(seconds=self.expiration_seconds)

    @property
    def seconds_left(self) -> int:
        return int((self.expires_at - timezone.now()).total_seconds())

    @property
    def is_expired(self):
        # TODO: -> NullBoolean property pseudo-field since these can't UNexpire?
        return self.seconds_left < 0


class UserToRundezvous(models.Model):
    """
    This model exists so old Rundezvouses can better reflect what happen
    TODO: Think up a better name
    """
    user = models.ForeignKey(
        SiteUser,
        on_delete=models.CASCADE,
    )
    rundezvous = models.ForeignKey(
        Rundezvous,
        on_delete=models.CASCADE,
    )

    is_active = models.BooleanField(
        default=True,
    )


class ChatMessage(models.Model):
    """
    Abstract ChatMessage, associated with a ChatRoom
    """
    class Meta:
        ordering = ('sent_at',)  # TODO: This might be unnecessary because sent_at should correlated with id

    room = models.ForeignKey(
        Rundezvous,
        on_delete=models.CASCADE,  # Message can't exist without room
        related_name='messages',
    )
    text = models.CharField(
        max_length=const.MAX_CHAT_MESSAGE_LENGTH,  # Twitter knew what they were doing I guess
    )
    sent_by = models.ForeignKey(
        SiteUser,
        on_delete=models.CASCADE,  # Message can't exist without user
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.sent_by} - {self.text}"
