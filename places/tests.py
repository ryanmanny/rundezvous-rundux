from django.test import TestCase

from django.contrib.gis.geos import Point, Polygon

from places import models


class TestSupportedRegionModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        polygon1 = Polygon((
            (0.0, 0.0),
            (0.0, 50.0),
            (50.0, 50.0),
            (50.0, 0.0),
            (0.0, 0.0),
        ))
        polygon2 = Polygon((
            (100.0, 100.0),
            (100.0, 150.0),
            (150.0, 150.0),
            (150.0, 100.0),
            (100.0, 100.0),
        ))

        cls.region1 = models.SupportedRegion.objects.create(
            name='Arbitrary Square 1',
            region=polygon1,
        )
        cls.region2 = models.SupportedRegion.objects.create(
            name='Arbitrary Square 2',
            region=polygon2,
        )

    def test_point_in_region(self):
        point_in_region1 = Point(25.0, 25.0)

        region = models.SupportedRegion.objects.get_for_point(point_in_region1)

        self.assertEqual(region, self.region1)

    def test_point_in_no_region(self):
        point_in_no_region = Point(-25.0, -25.0)

        with self.assertRaises(models.SupportedRegion.DoesNotExist):
            models.SupportedRegion.objects.get_for_point(point_in_no_region)
