import time

from unittest import skip

from .base import FunctionalTest, MatchingUsersFunctionalTest

from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys


class TestRegistration(FunctionalTest):
    def test_user_can_register(self):
        # Jimmy has heard of Rundezvous from a friend and wants to try it out
        # He is a skeptical guy and just wants to poke around
        self.browser.get(self.live_server_url)

        # Visiting the site, he sees a login page. He does not have an account,
        # but against his better judgment he decides to make one
        self.browser.find_element_by_id('signup_link').click()

        # He is now on the registration page, ready to make an account
        self.browser.find_element_by_id('id_username').send_keys('jimmy')

        self.browser.find_element_by_id('id_email').send_keys('jimmy@gmail.com')

        self.browser.find_element_by_id('id_password1').send_keys('bigboyjimbo')
        self.browser.find_element_by_id('id_password2').send_keys('bigboyjimbo')

        Select(self.browser.find_element_by_id('id_gender')).select_by_visible_text('Male')

        # Jimmy tries to enter 'funkmaster' as his name
        display_name = self.browser.find_element_by_id('id_display_name')
        display_name.send_keys('funkmaster')

        # However, he notices only one letter is allowed
        self.assertEqual('f', display_name.get_attribute('value'))

        self.browser.find_element_by_xpath("//button[@type='submit']").click()

        # After registering, he is now on the Rundezvous screen
        self.assertIn(
            'Start Rundezvous',
            self.browser.find_element_by_id('id_start_rundezvous').text
        )

        # Not liking the look of things, he does not start the Rundezvous
        # However, I sell his email to the Russians anyway


class TestRundezvous(MatchingUsersFunctionalTest):
    @skip
    def test_rundezvous(self):
        self.fail("Finish the test!")
