"""
Defines sensible admin panel for Chat app
"""

from django.contrib import admin
from django.urls import reverse

from django.utils.html import format_html

from chat import models


@admin.register(models.ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    model = models.ChatRoom

    class ChatMessageInline(admin.TabularInline):
        model = models.ChatMessage
        extra = 0  # Default number of blank messages to show

    inlines = [
        ChatMessageInline,  # To display messages associated with this ChatRoom
    ]

    @staticmethod
    def participants(obj):
        """
        Returns a string representing all users in ChatRoom, sep. by commas
        obj describes the current row being displayed
        """
        return ", ".join(
            str(participant)
            for participant
            in obj.participants
        )

    list_display = [
        'participants',
        'is_active',
    ]

    list_select_related = [
        # 'messages'  This would have to be a prefetch_related
    ]


@admin.register(models.ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    model = models.ChatMessage

    search_fields = [
        'sent_by__email',
    ]

    def room_link(self, obj):
        link = reverse("admin:chat_chatroom_change", args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', link, obj.room)

    list_display = [
        'room_link',
        'text',
        'sent_by',
        'sent_at',
    ]

    list_display_links = [
        'text'
    ]
