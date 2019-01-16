from django.conf import settings

from django.db import models

# Makes Chat app reusable
AUTH_USER_MODEL = settings.AUTH_USER_MODEL


class ChatRoom(models.Model):
    is_archived = models.BooleanField()


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,  # Message can't exist without room
        related_name='messages',
    )
    text = models.CharField(
        max_length=140,  # Twitter knew what they were doing I guess
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
    )
    sent_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Message can't exist without user
    )

    class Meta:
        # TODO: This might be unnecessary because sent_at correlated with id
        ordering = 'sent_at'
