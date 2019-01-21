from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from chat import models as chat_models

from rundezvous import managers as run_managers


class SiteUser(auth_models.AbstractUser):
    class Meta:
        verbose_name = "Site User"
        verbose_name_plural = "Site Users"

    email = models.EmailField(  # Overrides email field of AbstractUser
        unique=True,
        null=False,
        blank=False,
    )
    display_name = models.CharField(
        max_length=1,  # Identify users by single letter INNOVATION
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
    last_location = models.PointField(  # For position-based game elements
        verbose_name="Last Known Location",
        null=True,
        blank=True,
    )
    reputation = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.display_name if self.display_name else 'NONE'} - {self.email}>"
