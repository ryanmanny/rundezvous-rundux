from django.test import LiveServerTestCase
from django.test import tag


@tag('functional')
class FunctionalTest(LiveServerTestCase):
    def login(self, browser, username, password):
        browser.get(self.live_server_url)

        browser.find_element_by_id('id_username').send_keys(username)
        browser.find_element_by_id('id_password').send_keys(password)

        browser.find_element_by_xpath("//button[@type='submit']").click()
