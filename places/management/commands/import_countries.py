"""
https://docs.djangoproject.com/en/2.2/ref/contrib/gis/tutorial/#importing-spatial-countries
"""

from collections import defaultdict

import os

from django.core.management.base import BaseCommand

from django.contrib.gis.geos import fromstr, Polygon, MultiPolygon
from django.contrib.gis.gdal import DataSource

import places
from places import models
from places import const

countries_ds = DataSource(
    os.path.abspath(
        os.path.join(
            os.path.dirname(places.__file__),
            'data',
            'ne_10m_admin_0_countries',
            'ne_10m_admin_0_countries.shp',
        )
    )
)

states_ds = DataSource(
    os.path.abspath(
        os.path.join(
            os.path.dirname(places.__file__),
            'data',
            'ne_10m_admin_1_states_provinces',
            'ne_10m_admin_1_states_provinces.shp',
        )
    )
)


class Command(BaseCommand):
    help = 'Imports the Shapefiles into Countries and States'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all existing States and Countries to make room',
        )

    def handle(self, *args, **options):
        if 'delete' in options:
            models.Country.objects.all().delete()
            models.State.objects.all().delete()

        countries = {
            feature.get('name'): feature
            for feature in countries_ds[0]  # Shapefiles only have one layer
            if feature.get('name') in const.SUPPORTED_COUNTRIES
        }

        states = defaultdict(list)

        for feature in states_ds[0]:
            country = feature.get('admin')
            if country in countries:
                states[country].append(feature)

        for country_name, country_feature in countries.items():
            country_geo = fromstr(country_feature.geom.wkt)

            if isinstance(country_geo, Polygon):
                country_geo = MultiPolygon(country_geo)

            country = models.Country.objects.create(
                name=country_name,
                region=country_geo,
            )

            for state_feature in states[country_name]:
                state_geo = fromstr(state_feature.geom.wkt)

                if isinstance(state_geo, Polygon):
                    state_geo = MultiPolygon(state_geo)

                state = models.State.objects.create(
                    country=country,
                    name=state_feature.get('name'),
                    region=state_geo,
                )
