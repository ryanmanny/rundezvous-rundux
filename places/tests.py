from django.test import TestCase
from django.core.management import call_command

from django.contrib.gis.geos import Point, Polygon, MultiPolygon

from places import models


class TestCountryModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        polygon1 = MultiPolygon(
            Polygon((
                (0.0, 0.0),
                (0.0, 50.0),
                (50.0, 50.0),
                (50.0, 0.0),
                (0.0, 0.0),
            )),
        )
        polygon2 = MultiPolygon(
            Polygon((
                (100.0, 100.0),
                (100.0, 150.0),
                (150.0, 150.0),
                (150.0, 100.0),
                (100.0, 100.0),
            )),
        )

        cls.country1 = models.Country.objects.create(
            name='Arbitrary Square 1',
            region=polygon1,
        )
        cls.country2 = models.Country.objects.create(
            name='Arbitrary Square 2',
            region=polygon2,
        )

    def test_point_in_region(self):
        point_in_region1 = Point(25.0, 25.0)

        country = models.Country.objects.get_for_point(point_in_region1)

        self.assertEqual(country, self.country1)

    def test_point_in_no_region(self):
        point_in_no_region = Point(-25.0, -25.0)

        with self.assertRaises(models.Country.DoesNotExist):
            models.Country.objects.get_for_point(point_in_no_region)


class TestStateModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = models.Country.objects.create(
            name='Arbitrary Square Federation',
            region=MultiPolygon(
                Polygon((
                    (0.0, 0.0),
                    (0.0, 50.0),
                    (50.0, 50.0),
                    (50.0, 0.0),
                    (0.0, 0.0),
                )),
            ),
            projection_srid=1337,
        )

        cls.state = models.State.objects.create(
            name='Imperially Captured Arbitrary Square',
            region=MultiPolygon(
                Polygon((
                    (10.0, 10.0),
                    (10.0, 40.0),
                    (40.0, 40.0),
                    (40.0, 10.0),
                    (10.0, 10.0),
                )),
            ),
            country=cls.country,
        )

    def test_projection_srid_inheritance(self):
        self.assertEqual(self.state.projection_srid, 1337)

    def test_projection_srid_shadowing(self):
        self.state.projection_srid = 404
        self.state.save()

        self.assertEqual(self.state.projection_srid, 404)

# class TestImportCountries(TestCase):
#     def test_import_countries(self):
#         self.assertEqual(models.Country.objects.count(), 0)
#
#         call_command('import_countries')
#
#         self.assertNotEqual(models.Country.objects.count(), 0)
#
#     def test_import_countries_with_delete(self):
#         models.Country.objects.create(
#             name='Fake Country',
#             region=MultiPolygon(
#                 Polygon((
#                     (0.0, 0.0),
#                     (0.0, 50.0),
#                     (50.0, 50.0),
#                     (50.0, 0.0),
#                     (0.0, 0.0),
#                 ))
#             ),
#         )
#
#         call_command('import_countries')
#
#         with self.assertRaises(models.Country.DoesNotExist):
#             models.Country.objects.get(name='Fake Country')
