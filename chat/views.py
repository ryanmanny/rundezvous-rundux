from django.shortcuts import render

from chat import models


# TODO: Decorator that only allows participants to view
def chatroom(request, room_id):
    room = models.ChatRoom.objects.get(id=room_id)

    messages = [
        models.ChatMessage(
            text="HELLO",
        ),
        models.ChatMessage(
            text="GOODBYE",
        )
    ]

    render(
        request,
        'chatroom.html',
        {
            'messages': messages,
        }
    )
