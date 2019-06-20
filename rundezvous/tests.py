from django.test import TestCase

from django.shortcuts import reverse

from django.contrib.gis.geos import Point

from rundezvous import models


class UserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Don't store user on self since it won't get update
        cls.user_instance = models.SiteUser.objects.create(
            username='criminal_scum',
            email='inmate@private.prison',
            password='1234',
            location=Point(-117.1701676, 46.7316913),  # Honors Hall
        )

    def setUp(self):
        self.client.force_login(self.user_instance)

    @property
    def user(self):
        """Since storing self.user initially would mean using refresh_from_db"""
        user_id = self.client.session['_auth_user_id']
        return models.SiteUser.objects.get(id=user_id)


class TestUserLocationUpdateView(UserTestCase):
    def test_location_update_with_real_location(self):
        """
        Just tests if the update_location view works
        Testing the automatic functionality would require a functional test
        """
        response = self.client.post(
            reverse('update-location'),
            {
                'lat': 55.756496974,
                'long': 37.623664172,
            }
        )

        user = self.user

        self.assertNotEqual(user.location_updated_at, None)
        self.assertEqual(user.latitude, 55.756496974)
        self.assertEqual(user.longitude, 37.623664172)

    def test_location_update_with_missing_location(self):
        response = self.client.post(reverse('update-location'), follow=True)

        # User should be redirected to the location_required page
        self.assertTemplateUsed(response, 'rundezvous/location_required.html')
