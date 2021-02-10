from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from time import sleep
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

    def error_message_displayed(self, message=None):
        xpath = ""
        if message:
            xpath = wtxs.specific_error_message(message)
        else:
            xpath = wtxs.unspecified_error_message()
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

class StatusPage(Page):
    """This is the page object class for the Status page."""
    pass

class CloudsPage(Page):
    """This is the page object class for the Clouds page."""
    def __init__(self, driver):
        super(CloudsPage, self).__init__(driver)
        # The active_cloud variable stores the currently-selected cloud in the
        # sidebar.
        self.active_cloud = None
        self.active_metadata = None
    
    def click_add_button(self):
        wti.click_by_link_text(self.driver, '+')
        self.active_cloud = 'add_cloud'
        self.active_metadata = None

    def click_add_cloud(self):
        form = self.driver.find_element_by_id('new_cloud')
        text = form.get_attribute('value')
        self.driver.find_element_by_name('add_cloud').submit()
        self.active_cloud = text
        self.active_metadata = None

    def click_side_button(self, name):
        wti.click_by_link_text(self.driver, name)
        self.active_cloud = name
        self.active_metadata = None

    def click_side_tab(self, name):
        element_name = name.lower()
        xpath = wtxs.label_button(self.active_cloud, element_name)
        wti.click_by_xpath(self.driver, xpath)
        self.active_metadata = None

    def type_cloud_name(self, name):
        wti.fill_blank_by_id(self.driver, 'new_cloud', name)

    def click_enabled_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_cloud, 'enabled')
        wti.click_by_xpath(self.driver, xpath)

    def type_priority(self, priority):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'priority')
        wti.fill_blank_by_xpath(self.driver, xpath, priority)

    def select_cloud_type(self, type):
        xpath = wtxs.form_select_by_name(self.active_cloud, 'cloud_type')
        wti.select_option_by_xpath(self.driver, xpath, type)

    def type_url(self, url):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'authurl')
        wti.fill_blank_by_xpath(self.driver, xpath, url)

    def type_region(self, region):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'region')
        wti.fill_blank_by_xpath(self.driver, xpath, region)

    def type_project(self, project):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'project')
        wti.fill_blank_by_xpath(self.driver, xpath, project)

    def type_username(self, username):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'username')
        wti.fill_blank_by_xpath(self.driver, xpath, username)

    def type_password(self, password):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'password')
        wti.fill_blank_by_xpath(self.driver, xpath, password)

    def type_ca_certificate(self, certificate):
        xpath = wtxs.form_input_by_value(self.active_cloud, 'cacertificate')
        wti.fill_blank_by_xpath(self.driver, xpath, certificate)
        
    def type_user_domain_name(self, udn):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'user_domain_name')
        wti.fill_blank_by_xpath(self.driver, xpath, udn)

    def type_project_domain_name(self, pdn):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'project_domain_name')
        wti.fill_blank_by_xpath(self.driver, xpath, pdn)

    def type_boot_volume(self, boot_volume):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'vm_boot_volume')
        wti.fill_blank_by_xpath(self.driver, xpath, boot_volume)

    def add_security_group(self, group):
        wti.select_option_by_id(self.driver, 'rightValues-' + self.active_cloud, group)
        wti.click_by_id(self.driver, 'btnLeft-' + self.active_cloud)

    def remove_security_group(self, group):
        wti.select_option_by_id(self.driver, 'leftValues-' + self.active_cloud, group)
        wti.click_by_id(self.driver, 'btnRight-' + self.active_cloud)

    def select_vm_keyname(self, keyname):
        xpath = wtxs.form_select_by_name(self.active_cloud, 'vm_keyname')
        wti.select_option_by_xpath(self.driver, xpath, keyname)

    def select_vm_network(self, network):
        xpath = wtxs.form_select_by_name(self.active_cloud, 'vm_network')
        wti.select_option_by_xpath(self.driver, xpath, network)

    def select_vm_image(self, image):
        xpath = wtxs.form_select_by_name(self.active_cloud, 'vm_image')
        wti.select_option_by_xpath(self.driver, xpath, image)

    def select_vm_flavor(self, flavor):
        xpath = wtxs.form_select_by_name(self.active_cloud, 'vm_flavor')
        wti.select_option_by_xpath(self.driver, xpath, flavor)

    def type_vm_keep_alive(self, time):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'vm_keep_alive')
        wti.fill_blank_by_xpath(self.driver, xpath, time)

    def type_spot_price(self, price):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'vm_keep_alive')
        wti.fill_blank_by_xpath(self.driver, xpath, price)

    def type_cores_softmax(self, max):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'cores_softmax')
        wti.fill_blank_by_xpath(self.driver, xpath, max)

    def slide_cores_slider(self, value):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'cores_slider')
        slider = self.driver.find_element_by_xpath(xpath)
        wti.click_by_xpath(self.driver, xpath)
        offset = 1
        wti.slide_slider_by_xpath(self.driver, xpath, 2, 5)
        while int(slider.get_attribute('value')) < value:
            wti.slide_slider_by_xpath(self.driver, xpath, offset, 5)
            offset += 1

    def type_cores(self, value):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'cores_ctl')
        wti.fill_blank_by_xpath(self.driver, xpath, value)

    def increment_cores_by_arrows(self, value):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'cores_ctl')
        element = self.driver.find_element_by_xpath(xpath)
        start = int(element.get_attribute('value'))
        if start < value:
            for i in range(start, value):
                element.send_keys(Keys.ARROW_UP)
        else:
            for i in range(value, start):
                element.send_keys(Keys.ARROW_DOWN)

    def slide_ram_slider(self, value):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'ram_slider')
        slider = self.driver.find_element_by_xpath(xpath)
        wti.click_by_xpath(self.driver, xpath)
        offset = 1
        wti.slide_slider_by_xpath(self.driver, xpath, 2, 5)
        while int(slider.get_attribute('value')) < value:
            wti.slide_slider_by_xpath(self.driver, xpath, offset, 5)
            offset += 1

    def type_ram(self, value):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'ram_ctl')
        wti.fill_blank_by_xpath(self.driver, xpath, value)

    def increment_ram_by_arrows(self, value):
        xpath = wtxs.form_input_by_name(self.active_cloud, 'ram_ctl')
        element = self.driver.find_element_by_xpath(xpath)
        start = int(element.get_attribute('value'))
        if start < value:
            for i in range(start, value):
                element.send_keys(Keys.ARROW_UP)
        else:
            for i in range(value, start):
                element.send_keys(Keys.ARROW_DOWN)

    def click_update_cloud(self):
        self.driver.find_element_by_name(self.active_cloud).submit()

    def click_delete_button(self):
        wti.click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_cloud, self.active_cloud)
        wti.click_by_xpath(self.driver, xpath)
        self.active_cloud = None

    def click_metadata_new(self):
        xpath = wtxs.label_button(self.active_cloud, 'metadata-add')
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.frame('editor-' + self.active_cloud + '-add')
        self.active_metadata = 'add'

    def click_metadata(self, name):
        xpath = wtxs.label_button(self.active_cloud, 'metadata-' + name)
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.frame('editor-' + self.active_cloud + '-' + name)
        self.active_metadata = name

    def type_metadata_name(self, name):
        wti.fill_blank_by_name(self.driver, 'metadata_name', name)

    def click_metadata_enabled(self):
        xpath = wtxs.form_input_by_name_not_hidden('metadata-form', 'enabled')
        wti.click_by_xpath(self.driver, xpath)

    def type_metadata_priority(self, priority):
        wti.fill_blank_by_name(self.driver, 'priority', priority)

    def increment_metadata_priority_by_arrows(self, priority):
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'priority')))
        element = self.driver.find_element_by_name('priority')
        start = int(element.get_attribute('value'))
        if start < priority:
            for i in range(start, priority):
                element.send_keys(Keys.ARROW_UP)
        else:
            for i in range(priority, start):
                element.send_keys(Keys.ARROW_DOWN)
    
    def select_metadata_mime_type(self, type):
        wti.select_option_by_name(self.driver, 'mime_type', type)

    def type_metadata(self, metadata):
        wti.fill_blank_by_tag_name(self.driver, 'textarea', metadata)

    def click_metadata_add(self):
        form = self.driver.find_element_by_name('metadata_name')
        text = form.get_attribute('value')
        self.driver.find_element_by_name('metadata-form').submit()
        self.driver.switch_to.default_content()
        self.active_metadata = text

    def click_metadata_update(self):
        wti.click_by_id(self.driver, 'left')
        self.driver.switch_to.default_content()

    def click_metadata_delete(self):
        wti.click_by_id(self.driver, 'right')

    def click_metadata_delete_modal(self):
        xpath = wtxs.delete_button('metadata', self.active_metadata)
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.default_content()
        self.active_metadata = None

    def click_metadata_exclusions(self):
        xpath = wtxs.label_button(self.active_cloud, 'metadata-exclusions')
        wti.click_by_xpath(self.driver, xpath)

    def click_metadata_exclusions_checkbox(self, box):
        xpath = wtxs.form_input_by_value(self.active_cloud + '-metadata-exclusions', box)
        wti.click_by_xpath(self.driver, xpath)

    def click_update_metadata_exclusions(self):
        self.driver.find_element_by_name(self.active_cloud + '-metadata-exclusions').submit()

    def click_flavor_exclusions(self):
        xpath = wtxs.label_button(self.active_cloud, 'flavor-exclusions')
        wti.click_by_xpath(self.driver, xpath)

    def click_flavor_exclusions_checkbox(self, box):
        xpath = wtxs.form_input_by_value(self.active_cloud + '-flavor-exclusions', box)
        wti.click_by_xpath(self.driver, xpath)

    def click_update_flavor_exclusions(self):
        self.driver.find_element_by_name(self.active_cloud + '-flavor-exclusions').submit()
 
    def side_button_exists(self, name):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, name)))
            return True
        except TimeoutException:
            return False

    def enabled_box_checked(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_cloud, 'enabled')
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_located_to_be_selected((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

    def metadata_tab_exists(self, name):
        sleep(2)
        xpath = wtxs.label_button(self.active_cloud, 'metadata-' + name)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

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
    def __init__(self, driver):
        super(UsersPage, self).__init__(driver)
        # The active_user variable stores the currently-selected user in the
        # sidebar.
        self.active_user = None

    def click_add_button(self):
        wti.click_by_link_text(self.driver, '+')
        self.active_user = 'add_user'

    def click_add_user(self):
        form = self.driver.find_element_by_id('new_user')
        text = form.get_attribute('value')
        self.driver.find_element_by_id('new_user').submit()
        self.active_user = text

    def click_side_button(self, name):
        # This method uses the JavaScript click to avoid a Selenium bug with
        # clicking an element when another element's padding covers it.
        wtjsi.javascript_click_by_link_text(self.driver, name)
        self.active_user = name

    def type_user_name(self, name):
        wti.fill_blank_by_id(self.driver, 'new_user', name)

    def type_password(self, password, alt_password=None):
        if not alt_password:
            alt_password = password
        xpath1 = wtxs.form_input_by_name(self.active_user, 'password1')
        xpath2 = wtxs.form_input_by_name(self.active_user, 'password2')
        wti.fill_blank_by_xpath(self.driver, xpath1, password)
        wti.fill_blank_by_xpath(self.driver, xpath2, alt_password)

    def type_cert_cn(self, cert_cn):
        wti.fill_blank_by_name(self.driver, 'cert_cn', cert_cn)

    def click_superuser_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'is_superuser')
        wti.click_by_xpath(self.driver, xpath)

    def click_group_checkbox(self, group):
        xpath = wtxs.form_input_by_value(self.active_user, group)
        wti.click_by_xpath(self.driver, xpath)

    def click_update_user(self):
        self.driver.find_element_by_name(self.active_user).submit()

    def click_delete_button(self):
        wtjsi.javascript_click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_user, self.active_user)
        wti.click_by_xpath(self.driver, xpath)
        self.active_user = None

    def side_button_exists(self, name):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, name)))
            return True
        except TimeoutException:
            return False

    def group_box_checked(self, name):
        xpath = wtxs.form_input_by_value(self.active_user, name)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_located_to_be_selected((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

    def superuser_box_checked(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'is_superuser')
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_located_to_be_selected((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False


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
        wti.fill_blank_by_id(self.driver, 'new_group', name)

    def click_user_checkbox(self, user):
        xpath = wtxs.form_input_by_value(self.active_group, user)
        wti.click_by_xpath(self.driver, xpath)

    def type_in_search_bar(self, text):
        search_tag = ''
        if self.active_group and self.active_group is not 'add_group':
            search_tag = self.active_group
        wti.fill_blank_by_id(self.driver, 'search-users-' + search_tag, text)

    def click_update_group(self):
        self.driver.find_element_by_name(self.active_group).submit()

    def click_delete_button(self):
        wtjsi.javascript_click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_group, self.active_group)
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
        xpath = wtxs.form_input_by_value(self.active_group, name)
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
