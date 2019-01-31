from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from django.contrib.gis.measure import Distance

# Rundezvous depends on Chat, Places apps
from chat import models as chat_models
from places import models as place_models

from rundezvous import managers


class SiteUser(auth_models.AbstractUser):
    class Meta:
        verbose_name = "Site User"
        verbose_name_plural = "Site Users"

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
    active_room = models.ForeignKey(  # User can only access one room at a time
        chat_models.ChatRoom,
        null=True,  # User can exist without room
        blank=True,
        on_delete=models.SET_NULL,
    )
    reputation = models.IntegerField(
        default=0,
    )

    # LOCATION DATA
    last_location = models.PointField(  # For position-based game elements
        verbose_name="Last Known Location",
        null=True,
        blank=True,
    )
    last_region = models.ForeignKey(
        place_models.SupportedRegion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.display_name if self.display_name else 'NONE'} - {self.email}>"

    @property
    def is_in_supported_location(self):
        """Makes sure user is in a supported location
        TODO: Assert this is true every time location is updated
        """
        try:
            region = place_models.SupportedRegion.objects.get(
                region__intersects=self.last_location,
            )
        except place_models.SupportedRegion.DoesNotExist:
            self.last_region = None
            self.save()
            return False
        except place_models.SupportedRegion.MultipleObjectsReturned:
            # TODO: Consider overlapping regions, maybe log collisions here
            raise NotImplementedError
        else:
            self.last_region = region
            self.save()
            return True

    def users_within(self, distance: Distance):
        """Gets all users within distance miles of user
        """
        return SiteUser.objects.filter(
            last_region=self.last_region,  # Must be in same region
            last_location__distance_lt=(self.last_location, distance),
        ).distance(self.last_location)  # Annotates QuerySet with distance
