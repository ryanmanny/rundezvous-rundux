from django.conf import settings

from django.db import models

from django.contrib.auth import get_user_model
from django.db.models import Subquery


class ChatRoom(models.Model):
    class Meta:
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    is_active = models.BooleanField(
        default=True,
    )

    @property
    def participants(self):
        """Returns the User objects who have sent messages to this Room
        """
        return get_user_model().objects.filter(
            id__in=self.messages.values_list('sent_by_id', flat=True).distinct()
        )

    def archive(self):
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.participants}>"


class ChatMessage(models.Model):
    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

        ordering = ('sent_at',)  # TODO: This might be unnecessary because sent_at should correlated with id

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,  # Message can't exist without room
        related_name='messages',
    )
    text = models.CharField(
        max_length=140,  # Twitter knew what they were doing I guess
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Message can't exist without user
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.sent_by} - {self.text}>"
