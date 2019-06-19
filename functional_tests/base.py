from django.test import LiveServerTestCase
from django.test import tag


@tag('functional')
class FunctionalTest(LiveServerTestCase):
    pass
