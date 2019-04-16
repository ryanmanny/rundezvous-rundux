from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import (
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)

from chat import models
from chat import forms


@login_required
def chatroom(request):
    """
    Renders chatroom for the current user
    TODO: Render title in correct location
    """
    user = request.user

    room = user.active_room

    if room is None:
        return HttpResponseNotFound("You are not in any chatroom")

    return render(
        request,
        'chat/chatroom.html',
        {
            'form': forms.TextForm,
            'user': user,
            'room': room,
            'room_name': room.name,
        },
    )


@login_required
def new_messages(request, last_message_id):
    """
    Bad polling function to get messages since the last one the user knows of
    TODO: This MUST be replaced with RabbitMQ or Django Channels
    """
    user = request.user

    room = user.active_room

    messages = room.messages.filter(id__gt=last_message_id)

    return JsonResponse({
        'message_ids': list(messages.values_list('id', flat=True))
    })


@login_required
def message(request, message_id=None):
    """
    TODO: Should this be two views?
    TODO: Make this a class-based view?
    """
    user = request.user
    room = user.active_room  # Make sure user can only get msg from his room

    if request.method == "GET":
        try:
            message = models.ChatMessage.objects.get(
                room=room,
                id=message_id,
            )
        except models.ChatMessage.DoesNotExist:
            return HttpResponseNotFound
    elif request.method == "POST":
        assert message_id is None

        text = request.POST['text']

        message = models.ChatMessage.objects.create(
            text=text,
            sent_by=user,
            room=room,
        )
    else:
        return HttpResponseBadRequest

    return render(
        request,
        'chat/message.html',
        {
            'message': message,
            'user': user,
        }
    )
