from django.contrib.gis.db import models as models
from django.contrib.auth import models as auth_models

from chat import models as chat_models

from rundezvous import managers as run_managers


class SiteUser(auth_models.AbstractUser):
    objects = run_managers.SiteUserManager.from_queryset(run_managers.SiteUserSet)

    display_name = models.CharField(
        max_length=1,  # Identify users by single letter INNOVATION
    )
    # display_color TODO: Import django-colorpicker
    active_room = models.ForeignKey(  # User can only access one room at a time
        chat_models.ChatRoom,
        null=True,  # User can exist without room
        blank=True,
        on_delete=models.SET_NULL,
        related_name='active_participants',  # TODO: Might be coupling
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
        return f"<SiteUser {self.display_name} - {self.email}>"
