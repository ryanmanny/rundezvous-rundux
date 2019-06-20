from abc import ABCMeta

from selenium import webdriver

from model_mommy import mommy

from django.test import LiveServerTestCase
from django.test import tag

from rundezvous.models import SiteUser


def create_user(gender):
    """Creates straight users because it's easy for me to keep straight"""
    likes_females = (gender == SiteUser.MALE)
    likes_males = (gender == SiteUser.FEMALE)

    password = 'password'

    user = mommy.make('rundezvous.SiteUser', gender=gender)
    user.set_password(password)
    user.save()

    mommy.make(
        'rundezvous.Preferences',
        user=user,
        males=likes_males, females=likes_females, hookups=True,
    )

    return user.username, password


@tag('functional')
class AbstractFunctionalTest(LiveServerTestCase, metaclass=ABCMeta):
    def login(self, username, password, browser=None):
        if browser is None:
            browser = self.browser

        browser.get(self.live_server_url)

        browser.find_element_by_id('id_username').send_keys(username)
        browser.find_element_by_id('id_password').send_keys(password)

        browser.find_element_by_xpath("//button[@type='submit']").click()


class FunctionalTest(AbstractFunctionalTest):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.close()


class LoggedInFunctionalTest(FunctionalTest):
    """Logs a user in in advance"""
    def setUp(self):
        super().setUp()
        self.login(*create_user(SiteUser.MALE))


class MatchingUsersFunctionalTest(AbstractFunctionalTest):
    """Opens two browsers owned by two users who would match"""
    def setUp(self):
        self.male = webdriver.Firefox()
        self.login(*create_user(SiteUser.MALE), browser=self.male)

        self.female = webdriver.Firefox()
        self.login(*create_user(SiteUser.FEMALE), browser=self.female)

    def tearDown(self):
        self.male.quit()
        self.female.quit()
