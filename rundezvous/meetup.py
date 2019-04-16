from django.contrib.gis.geos import Point
# https://docs.djangoproject.com/en/2.1/ref/contrib/gis/functions
from django.contrib.gis.db.models.functions import Centroid
# https://docs.djangoproject.com/en/2.1/ref/contrib/gis/geoquerysets
from django.contrib.gis.db.models.aggregates import Collect


def get_midpoint(user_set) -> Point:
    return user_set.aggregate(
        midpoint=Centroid(  # Centroid calculates the midpoint of a Geometry
            Collect('last_location')
        )
    )['midpoint']
