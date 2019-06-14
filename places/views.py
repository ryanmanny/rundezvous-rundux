from django.contrib.auth import logout

from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from django.contrib.gis.geos.point import Point

from places import const


def geo_test(request):
    """
    A crappy test endpoint to display current coords
    """
    return render(request, 'places/geo_test.html', {})


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

    # Longitude is x, Latitude is y
    location = Point(long, lat, srid=const.DEFAULT_SRID)

    user = request.user

    location_changed = user.location != location

    if location_changed:  # This might be useless
        user.update_location(location)

    return JsonResponse({
        'update': location_changed,
        'success': True,
    })
