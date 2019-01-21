from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseForbidden, Http404

from chat import models
from chat import forms


@login_required
def chatroom(request):
    user = request.user

    room = user.active_room

    if room is None:
        return Http404()

    room_name = ", ".join(
        participant.display_name or "NONE"
        for participant
        in room.participants - {user}
    )

    return render(
        request,
        'chat/chatroom.html',
        {
            'form': forms.TextForm,
            'user': user,
            'room': room,
            'room_name': room_name,
        },
    )


@login_required
def new_messages(request, last_message_id):
    user = request.user

    room = user.active_room

    messages = room.messages.filter(id__gt=last_message_id)

    return JsonResponse({
        'message_ids': list(messages.values_list('id', flat=True))
    })


@login_required
def message(request, message_id=None):
    user = request.user
    room = user.active_room

    if request.method == "GET":
        try:
            message = models.ChatMessage.objects.get(
                room=room,
                id=message_id,
            )
        except models.ChatMessage.DoesNotExist:
            return HttpResponseForbidden
        else:
            return render(
                request,
                'chat/message.html',
                {
                    'message': message,
                    'right_align': user == message.sent_by,
                }
            )

    if request.method == "POST":
        assert message_id is None

        text = request.POST['text']

        models.ChatMessage.objects.create(
            text=text,
            sent_by=user,
            room=room,
        )

        return JsonResponse({
            'success': True,
        })
