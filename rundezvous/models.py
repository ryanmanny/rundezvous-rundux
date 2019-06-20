from typing import Iterable

from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from django.contrib.gis.db.models import Subquery

from django.utils import timezone
from django.contrib.gis import measure

from django.core.validators import MinValueValidator, MaxValueValidator

# Rundezvous depends on Chat, Places apps
from places import models as place_models
from places import const as place_const

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

    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'

    gender = models.CharField(
        max_length=1,
        choices=[
            (MALE, 'Male'),
            (FEMALE, 'Female'),
            (OTHER, 'Other'),
        ],
        default=FEMALE,  # Female is actually the default biological gender
    )
    # display_color TODO: Import django-colorpicker
    reputation = models.IntegerField(
        default=0,
    )

    # LOCATION DATA
    location = models.PointField(  # For position-based game elements
        verbose_name="last known location",
        null=True,
        blank=True,
        srid=place_const.DEFAULT_SRID,
    )
    state = models.ForeignKey(
        place_models.State,
        verbose_name="last known state",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    location_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,  # To get active users quickly
    )

    # RUNDEZVOUS DATA
    class Status:
        NONE = 'N'
        LOOKING = 'L'
        CHATTING = 'C'
        RUNNING = 'R'
        REVIEW = 'V'

    status = models.CharField(
        # This field is used to filter users based on what they're doing
        # TODO: Formalize this into the State Pattern?
        max_length=1,
        choices=[
            (Status.NONE, 'None'),
            (Status.LOOKING, 'Looking'),
            (Status.CHATTING, 'Chatting'),
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
        return f"{self.email} ({self.display_name or '?'})"

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    @property
    def active_rundezvous(self):
        try:
            return self.usertorundezvous_set.get(
                is_active=True,
            ).rundezvous
        except UserToRundezvous.DoesNotExist:
            return None
        except UserToRundezvous.MultipleObjectsReturned:
            # TODO: Figure out what to do here, this is bad but possible
            raise

    @property
    def unmet_users(self):
        return SiteUser.objects. \
            filter(state=self.state). \
            exclude(id=self.id). \
            exclude(id__in=Subquery(self.met_users.values_list('id', flat=True)))

    def update_location(self, new_location):
        """
        Called by the middleware to update user's location
        """
        self.location = new_location
        self.location_updated_at = timezone.now()

        self.save()

        if self.active_rundezvous and self.check_rundezvous_arrived():
            self.handle_rundezvous_arrival()

    def check_rundezvous_arrived(self):
        """Returns whether user is within threshold of Rundezvous"""
        # The user's location is stored in lat long (srid=4326) so it must be
        # transformed into a coordinate system measure in meters before the
        # distance between the two points can be calculated
        srid = self.state.projection_srid  # The default

        location = self.location. \
            transform(srid, clone=True)
        landmark_location = self.active_rundezvous.landmark.location. \
            transform(srid, clone=True)
        distance = location.distance(landmark_location)

        return measure.Distance(m=distance) < const.MEETUP_DISTANCE_THRESHOLD

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

    def get_meetable_users_within(self, distance: measure.Distance):
        """
        Gets all users less than distance miles away from user
        Used to find the next user to match with
        """
        return self.unmet_users.filter_by_active().filter(
            location__distance_lte=(self.location, distance),
            status=SiteUser.Status.LOOKING,
        ).order_by_closest_to(self)

    def find_rundezvous_partner(self):
        """Returns closest eligible user"""
        partner = self. \
            get_meetable_users_within(const.MEETUP_DISTANCE_THRESHOLD).first()

        if partner is None:
            raise SiteUser.DoesNotExist
        else:
            return partner

    def make_meetup_decision(self, decision: bool):
        rundezvous = self.active_rundezvous
        utr = self.usertorundezvous_set.get(rundezvous=rundezvous)

        if timezone.now() < rundezvous.meet_decision_ends_at:
            utr.meetup_decision = decision
            utr.save()
        else:
            raise Rundezvous.DecisionTimeoutError


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

    def __str__(self):
        return f"{self.user}'s {self._meta.verbose_name}"


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

    def __str__(self):
        return f"{self.reviewer} reviewed {self.reviewed}"


class Rundezvous(models.Model):
    """
    The titular unit of countries, describes the meetup between two+ users
    When a Rundezvous is first created it is just a Chatroom
    """
    class Meta:
        verbose_name_plural = 'rundezvouses'  # (nonstandard, rare)

    objects = managers.RundezvousManager()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    started_at = models.DateTimeField(  # Used to time out users
        default=None,
        null=True,
        blank=True,
    )
    ended_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
    )

    landmark = models.ForeignKey(
        place_models.Landmark,
        null=True,
        blank=True,
        on_delete=models.CASCADE,  # Meetup needs a location
    )
    expiration_seconds = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(const.MAX_RUNDEZVOUS_EXPIRATION.seconds),
        ]
    )

    # TODO: Add archival logic

    def __str__(self):
        return f"{[u for u in self.users.all()]} meeting at {self.landmark}"

    class DecisionTimeoutError(TimeoutError):
        pass

    class RunTimeError(TimeoutError):
        pass

    @property
    def chat_ends_at(self) -> timezone.datetime:
        return self.created_at + const.CHAT_TIME_LIMIT

    @property
    def meet_decision_ends_at(self) -> timezone.datetime:
        return self.created_at + \
               const.CHAT_TIME_LIMIT + const.MEET_DECISION_TIME_LIMIT

    @property
    def expires_at(self) -> timezone.datetime:
        if self.landmark is not None:
            return self.started_at + \
                   timezone.timedelta(seconds=self.expiration_seconds)
        else:
            raise place_models.Landmark.DoesNotExist

    @property
    def seconds_left(self) -> int:
        """This will also be computed in the GUI if I'm not insane"""
        return int((self.expires_at - timezone.now()).total_seconds())

    @property
    def is_expired(self):
        return self.seconds_left < 0

    @classmethod
    def create_for_users(cls, users: Iterable[SiteUser]):
        """
        Create a Rundezvous, and add all of the users to it
        This should work for any number of users, even just one
        """
        rundezvous = cls.objects.create()

        for user in users:
            user.rundezvouses.add(  # Pycharm is mistaken here
                rundezvous,
                through_defaults={'is_active': True},
            )
            user.rundezvous_status = SiteUser.Status.CHATTING
            user.save()

    def start_meetup(self):
        """
        Sets the closest landmark as the destination, then starts the timer
        """
        if not self.users.exists():
            raise SiteUser.DoesNotExist

        users = self.users

        state = users.first().state  # Assume they're all in the same state
        midpoint = users.get_midpoint()

        # Get closest Landmark
        landmark = place_models.Landmark.objects.filter(state=state) \
            .order_by_closest_to(midpoint).first()

        self.landmark = landmark
        self.started_at = timezone.now()
        self.expiration_seconds = 600  # TODO: Calculate this somehow
        self.save()


class UserToRundezvous(models.Model):
    """
    This model exists so old Rundezvouses can better reflect what happened
    TODO: Think up a better name
    """
    class Meta:
        verbose_name_plural = 'user to rundezvouses'

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

    meetup_decision = models.NullBooleanField(
        default=None,
    )


class ChatMessage(models.Model):
    """
    Abstract ChatMessage, associated with a ChatRoom
    """
    class Meta:
        ordering = ('sent_at',)

    room = models.ForeignKey(
        Rundezvous,
        on_delete=models.CASCADE,  # Message can't exist without room
        related_name='messages',
    )
    text = models.CharField(
        # Twitter knew what they were doing I guess
        max_length=const.MAX_CHAT_MESSAGE_LENGTH,
    )
    sent_by = models.ForeignKey(
        SiteUser,
        on_delete=models.CASCADE,  # Message can't exist without user
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.sent_by} says "{self.text}"'
