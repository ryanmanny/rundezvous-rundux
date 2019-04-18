from django.shortcuts import render


def geo_test(request):
    return render(request, 'places/geo_test.html', {})
