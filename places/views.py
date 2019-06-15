from django.shortcuts import render


def geo_test(request):
    """
    A crappy test endpoint to display current coords
    """
    return render(request, 'places/geo_test.html', {})
