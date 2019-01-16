"""
Defines sensible admin panel for Chat app
"""

from django.contrib import admin

from chat import models


class ChatRoomAdmin(admin.ModelAdmin):
    model = models.ChatRoom

    class ChatMessageInline(admin.TabularInline):
        model = models.ChatMessage

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
            set(
                f"{participant}"
                for participant
                in obj.partipants.distinct()
            )
        )

    list_display = [
        participants,
    ]

    list_select_related = [
        'participants',  # Should reduce participants # queries I hope
    ]


admin.register(ChatRoomAdmin)
