from django.contrib.gis.geos.point import Point

from django.contrib.auth import logout

from django.shortcuts import render
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


def geo_test(request):
    """
    A crappy test endpoint to display current coords
    """
    return render(request, 'places/geo_test.html', {})


@csrf_exempt
def update_location(request):
    """
    Update a user's location
    """
    lat = float(request.POST.get('lat'))
    long = float(request.POST.get('long'))

    # Longitude is x, Latitude is y
    location = Point(long, lat, srid=4326)

    user = request.user

    if not location:
        # Location services must be on
        logout(request)
        return JsonResponse({
            'error': 'Location Services must be enabled',
            'success': False,
        }, status=500)

    location_changed = user.location != location

    if location_changed:  # This might be useless
        user.update_location(location)

    return JsonResponse({
        'update': location_changed,
        'success': True,
    })
