from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import web_tests.web_test_interactions as wti
import web_tests.web_test_javascript_interactions as wtjsi
import web_tests.web_test_xpath_selectors as wtxs

# This module contains the page objects (classes to represent pages) for the
# unittest web tests.

class Page(object):
    """This is the base page class, which all pages inherit from. It contains
       methods for page functions all pages have."""

    def __init__(self, driver):
        self.driver = driver

    def click_top_nav(self, name):
        wti.click_by_link_text(self.driver, name)

class StatusPage(Page):
    """This is the page object class for the Status page."""
    pass

class CloudsPage(Page):
    """This is the page object class for the Clouds page."""
    pass

class AliasesPage(Page):
    """This is the page object class for the Aliases page."""
    pass

class DefaultsPage(Page):
    """This is the page object class for the Defaults page."""
    pass

class ImagesPage(Page):
    """This is the page object class for the Images page."""
    pass

class KeysPage(Page):
    """This is the page object class for the Keys page."""
    pass

class UsersPage(Page):
    """This is the page object class for the Users page."""
    pass

class GroupsPage(Page):
    """This is the page object class for the Groups page."""

    def __init__(self, driver):
        super(GroupsPage, self).__init__(driver)
        # The active_group variable stores the currently-selected group in the
        # sidebar. 
        self.active_group = None

    def click_add_button(self):
        wti.click_by_link_text(self.driver, '+')
        self.active_group = 'add_group'

    def click_add_group(self):
        form = self.driver.find_element_by_id('new_group')
        text = form.get_attribute('value')
        self.driver.find_element_by_id('new_group').submit()
        self.active_group = text

    def click_side_button(self, name):
        # This method uses the JavaScript click to avoid a Selenium bug with
        # clicking an element when another element's padding covers it.
        wtjsi.javascript_click_by_link_text(self.driver, name)
        self.active_group = name

    def type_group_name(self, name):
        wti.fill_blank(self.driver, 'new_group', name)

    def click_user_checkbox(self, user):
        xpath = wtxs.user_checkbox(self.active_group, user)
        wti.click_by_xpath(self.driver, xpath)

    def type_in_search_bar(self, text):
        search_tag = ''
        if self.active_group and self.active_group is not 'add_group':
            search_tag = self.active_group
        wti.fill_blank(self.driver, 'search-users-' + search_tag, text)

    def click_update_group(self):
        self.driver.find_element_by_name(self.active_group).submit()

    def click_delete_button(self):
        wtjsi.javascript_click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_group)
        wti.click_by_xpath(self.driver, xpath)
        self.active_group = None

    def side_button_exists(self, name):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, name)))
            return True
        except TimeoutException:
            return False

    def box_checked(self, name):
        xpath = wtxs.user_checkbox(self.active_group, name)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_located_to_be_selected((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

class ConfigPage(Page):
    """This is the page object class for the Config page."""
    pass

class SettingsPage(Page):
    """This is the page object class for the User Settings page."""
    pass
