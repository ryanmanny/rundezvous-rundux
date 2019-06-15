from django.shortcuts import render, redirect, reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

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
        return redirect(reverse('waiting_room'))
    elif user.status == models.SiteUser.Status.CHATTING:
        return redirect(reverse('chatroom'))
    elif user.status == models.SiteUser.Status.RUNNING:
        return redirect(reverse('active_rundezvous'))
    elif user.status == models.SiteUser.Status.REVIEW:
        return redirect(reverse('review'))
    else:
        raise NotImplementedError


@login_required
def waiting_room(request):
    """Waiting room for the user while the next Rundezvous is found"""
    raise NotImplementedError


@login_required
def active_rundezvous(request):
    """
    Screen displayed while the user is running to the destination
    Will show Google Maps frame, and will automatically detect arrival
    """
    return render(
        request,
        'rundezvous/active_rundezvous.html',
        {
            'rundezvous': request.user.active_rundezvous,
        },
    )


@login_required
def review(request):
    """Form for the user to review partner from previous Rundezvous"""
    raise NotImplementedError
