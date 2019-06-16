from django.http import JsonResponse

from django.shortcuts import render, redirect, reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

from django.contrib.gis.geos import Point

from rundezvous import models
from rundezvous import forms

from places import const as place_const


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


@csrf_exempt
def update_location(request):
    """
    Update a user's location
    This would be pretty easy to spoof TODO: Analyze if that would be a problem
    """
    try:
        lat = float(request.POST.get('lat'))
        long = float(request.POST.get('long'))
    except TypeError:
        # Location services must be on
        return redirect(reverse('location_required'))

    user = request.user

    # Longitude is x, Latitude is y
    location = Point(long, lat, srid=place_const.DEFAULT_SRID)

    location_changed = user.location != location

    if location_changed:  # This might be useless
        user.update_location(location)

    return JsonResponse({
        'update': location_changed,
        'success': True,
    })


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