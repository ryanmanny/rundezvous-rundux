from django.http import (
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)

from django.shortcuts import render, redirect, reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from rundezvous import const
from rundezvous import models
from rundezvous import forms


def home(request):
    if request.user.is_anonymous:
        return redirect(reverse('login'))
    else:
        return redirect(reverse('rundezvous_router'))


def signup(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('home')
    else:
        form = forms.SignupForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def location_required(request):
    return render(request, 'rundezvous/location_required.html')


@login_required
def rundezvous_router(request):
    """Routes user to appropriate destination based on their status"""
    user = request.user

    if user.status == models.SiteUser.Status.NONE:
        user.status = models.SiteUser.Status.LOOKING
        user.save()

    if user.status == models.SiteUser.Status.LOOKING:
        pass
    elif user.status == models.SiteUser.Status.CHATTING:
        pass
    elif user.status == models.SiteUser.Status.RUNNING:
        pass
    elif user.status == models.SiteUser.Status.REVIEW:
        pass

    raise NotImplementedError


@login_required
def chatroom(request):
    """
    Renders Chatroom for the current user
    TODO: Make this a class-based View?
    """
    user = request.user

    room = user.active_rundezvous

    if room is None:
        return HttpResponseNotFound("You are not in any chatroom")

    return render(
        request,
        'rundezvous/chatroom/chatroom.html',
        {
            'user': user,
            'room': room,
            'max_message_len': const.MAX_CHAT_MESSAGE_LENGTH,
            'time_limit': const.CHAT_TIME_LIMIT,
        },
    )


@login_required
def active_rundezvous(request):
    user = request.user

    return render(request, 'rundezvous/active_rundezvous.html', {
        'rundezvous': user.active_rundezvous,
    })


@login_required
def chatroom(request):
    """
    Renders ChatRoom for the current user
    TODO: Render title in correct location
    """
    user = request.user

    room = user.active_room

    if room is None:
        return HttpResponseNotFound("You are not in any chatroom")

    return render(
        request,
        'rundezvous/chatroom/chatroom.html',
        {
            'user': user,
            'room': room,
            'max_message_len': const.MAX_CHAT_MESSAGE_LENGTH,
        },
    )


@login_required
def new_messages(request, last_message_id):
    """
    Bad polling function to get messages since the last one the user has
    It's also very easily abusable
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
        'rundezvous/chatroom/message.html',
        {
            'message': message,
            'user': user,
        }
    )
