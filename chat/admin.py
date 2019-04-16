"""
Defines sensible admin panel for Chat app
"""

from django.contrib import admin
from django.urls import reverse

from django.utils.html import format_html

from chat import models


@admin.register(models.ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """
    Displays a ChatRoom along with all messages sent
    TODO: Optimize queries to avoid O(N) exponential explosion
    """
    model = models.ChatRoom

    class ChatMessageInline(admin.TabularInline):
        model = models.ChatMessage
        extra = 0  # Default number of blank messages to show

    inlines = [
        ChatMessageInline,  # To display messages associated with this ChatRoom
    ]

    @staticmethod
    def room_name(obj):
        """
        Returns a string representing all users in ChatRoom, sep. by commas
        obj describes the current row being displayed
        """
        return obj.name

    list_display = [
        'room_name',
        'is_active',
    ]

    list_select_related = [
        # 'siteuser_set',
        # 'messages',  # These would have to be a prefetch_related
    ]


@admin.register(models.ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Displays a ChatMessage, and link to edit its corresponding ChatRoom
    """
    model = models.ChatMessage

    search_fields = [
        'sent_by__email',
    ]

    @staticmethod
    def room_link(obj):
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
