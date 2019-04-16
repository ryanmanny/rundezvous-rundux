from django.conf import settings

from django.db import models

from chat.const import MAX_MESSAGE_LENGTH


class ChatRoom(models.Model):
    """
    Represents an abstract ChatRoom, accessible to user's based on user.active_room
    """
    is_active = models.BooleanField(
        default=True,
    )

    @property
    def name(self):
        """
        Joins names of all participants in room together
        """
        return ", ".join(user.display_name for user in self.siteuser_set.all())

    def archive(self):
        """
        Set to True when no users can access anymore
        """
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self._meta.verbose_name} <{self.name}>"


class ChatMessage(models.Model):
    """
    Abstract ChatMessage, associated with a ChatRoom
    """
    class Meta:
        ordering = ('sent_at',)  # TODO: This might be unnecessary because sent_at should correlated with id

    room = models.ForeignKey(
        'ChatRoom',
        on_delete=models.CASCADE,  # Message can't exist without room
        related_name='messages',
    )
    text = models.CharField(
        max_length=MAX_MESSAGE_LENGTH,  # Twitter knew what they were doing I guess
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
