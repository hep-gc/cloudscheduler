from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from time import sleep
import web_tests.web_test_interactions as wti
import web_tests.web_test_javascript_interactions as wtjsi
import web_tests.web_test_xpath_selectors as wtxs
import web_tests.web_test_helpers as helpers

# This module contains the page objects (classes to represent pages) for the
# unittest web tests.

class Page(object):
    """This is the base page class, which all pages inherit from. It contains
       methods for page functions all pages have."""

    def __init__(self, driver):
        self.driver = driver

    def click_top_nav(self, name):
        wti.click_by_link_text(self.driver, name)

    def switch_default_group(self, group):
        wti.select_option_by_name(self.driver, 'group', group)

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
    def __init__(self, driver):
        super(StatusPage, self).__init__(driver)
        # There may be variables here in the future, currently unknown

    def click_jobs_group_expand(self, group):
        xpath = wtxs.status_page_dropdown('1', group)
        wti.click_by_xpath(self.driver, xpath)

    def click_job_data_box(self, group, state):
        state_tag = '_' + state.lower()
        if state == 'Jobs':
            state_tag = ''
        path = group + ' jobs' + state_tag
        xpath = wtxs.data_box(path)
        wti.click_by_xpath(self.driver, xpath)

    def click_vms_group_expand(self, group):
        xpath = wtxs.status_page_dropdown('2', group)
        wti.click_by_xpath(self.driver, xpath)

    def click_vms_cloud_expand(self, cloud):
        xpath = wtxs.status_page_dropdown('2', cloud)
        wti.click_by_xpath(self.driver, xpath)

    def click_vm_data_box(self, group, cloud, state):
        state_tag = '_' + state.lower()
        if state == 'VMs':
            state_tag = ''
        if state == 'Error':
            state_tag = '_in_error'
        if cloud == 'Totals':
            state_tag += '_total'
            path = 'VMs' + state_tag
        else:
            path = group + ' ' +  cloud + ' VMs' + state_tag
        xpath = wtxs.data_box(path)
        wti.click_by_xpath(self.driver, xpath)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'plot-container')))

    def click_slot_data_box(self, group, cloud, state):
        state_tag = '_' + state.lower()
        if state == 'Slots':
            state_tag = '_count'
        if state == 'Busy':
            state_tag = '_core_count'
        if state == 'Idle':
            state_tag = '_idle_core_count'
        if cloud == 'Totals':
            state_tag += '_total'
            path = 'slot' + state_tag
        else:
            path = group + ' ' + cloud + ' slot' + state_tag
        xpath = wtxs.data_box(path)
        wti.click_by_xpath(self.driver, xpath)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'plot-container')))

    def click_native_cores_data_box(self, group, cloud, state):
        state_tag = '_' + state.lower()
        if state == 'Used':
            state_tag = '_native'
        if cloud == 'Totals':
            state_tag += '_total'
            path = 'cores' + state_tag
        else:
            path = group + ' ' + cloud + ' cores' + state_tag
        xpath = wtxs.data_box(path)
        wti.click_by_xpath(self.driver, xpath)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'plot-container')))

    def click_ram_data_box(self, group, cloud):
        xpath = wtxs.data_box(group + ' ' + cloud + ' ' + 'ram_native')
        wti.click_by_xpath(self.driver, xpath)

    def select_plot_range(self, range):
        xpath = wtxs.div_a_by_text('myDropdown', range)
        wti.click_by_id(self.driver, 'range-select')
        wti.click_by_xpath(self.driver, xpath)

    def click_plot_legend_item(self, item):
        xpath = wtxs.legend_item(item)
        wti.click_by_xpath(self.driver, xpath)

    def click_close_plot(self):
        wti.click_by_id(self.driver, 'close-plot')

    def job_group_expanded(self, group):
        element = self.driver.find_element_by_id('expand-jobs-' + group.lower())
        return element.is_displayed()

    def vm_group_expanded(self, group):
        xpath = wtxs.vm_expand(group)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            return False
        element = self.driver.find_element_by_xpath(xpath)
        return element.is_displayed()

    def vm_cloud_expanded(self, group, cloud):
        if cloud == 'Totals':
            cloud = ''
        element = self.driver.find_element_by_id('expand-' + group + '-' + cloud)
        return element.is_displayed()

    def plot_open(self):
        element = self.driver.find_element_by_id('plot')
        return element.is_displayed()

    def first_date_on_plot_before_now(self, time, units, margin):
        sleep(5)
        xpath = wtxs.axis_data_point('xtick')
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        element = self.driver.find_element_by_xpath(xpath) 
        chart_date = helpers.parse_datetime(element.text)
        test_date = helpers.time_before(time, units)
        print(test_date)
        test_date = helpers.round_date(test_date, margin, True)
        if margin > 30:
            test_date = test_date.replace(day=1)
        print(chart_date)
        print(test_date)
        return chart_date.date() == test_date.date()

    def first_time_on_plot_before_now(self, time, units, margin):
        sleep(5)
        xpath = wtxs.axis_data_point('xtick')
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        element = self.driver.find_element_by_xpath(xpath)
        chart_time = helpers.parse_datetime(element.text)
        test_time = helpers.time_before(time, units)
        test_time = helpers.round_datetime(test_time, margin*60, True)
        return chart_time == test_time

    def last_date_on_plot_before_now(self, time, units, margin):
        xpath = wtxs.axis_data_point('xtick')
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        elements = self.driver.find_elements_by_xpath(xpath)
        chart_date = helpers.parse_datetime(element.text)
        test_date = helpers.time_before(time, units)
        test_date = helpers.round_date(test_date, margin, False)
        return chart_date.date() == test_date.date()

    def last_time_on_plot_before_now(self, time, units):
        xpath = wtxs.axis_data_point('xtick')
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        elements = self.driver.find_elements_by_xpath(xpath)
        element = elements[-1]
        chart_time = helpers.parse_datetime(element.text)
        test_time = helpers.time_before(0, 'minutes')
        test_time = helpers.round_datetime(test_time, margin*60, False)
        return chart_time == test_time

    def plot_has_legend(self, legend):
        xpath = wtxs.legend_item(legend)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

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
        xpath = wtxs.form_submit_by_value('add_cloud', 'Add Cloud')
        wti.click_by_xpath(self.driver, xpath)
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
        xpath = wtxs.form_submit_by_value(self.active_cloud, 'Update Cloud')
        wti.click_by_xpath(self.driver, xpath)

    def click_delete_button(self):
        wti.click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_cloud, self.active_cloud)
        wti.click_by_xpath(self.driver, xpath)
        self.active_cloud = None

    def click_delete_cancel(self):
        xpath = wtxs.delete_cancel(self.active_cloud)
        wti.click_by_xpath(self.driver, xpath)

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
        xpath = wtxs.form_input_by_value('metadata-form', 'Add')
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.default_content()
        if self.metadata_tab_exists(text):
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

    def click_metadata_delete_cancel(self):
        xpath = wtxs.delete_cancel('metadata')
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.default_content()

    def click_metadata_exclusions(self):
        xpath = wtxs.label_button(self.active_cloud, 'metadata-exclusions')
        wti.click_by_xpath(self.driver, xpath)

    def click_metadata_exclusions_checkbox(self, box):
        xpath = wtxs.form_input_by_value(self.active_cloud + '-metadata-exclusions', box)
        wti.click_by_xpath(self.driver, xpath)

    def click_update_metadata_exclusions(self):
        xpath = wtxs.form_submit_by_value(self.active_cloud + '-metadata-exclusions', 'Update Metadata Exclusions')
        wti.click_by_xpath(self.driver, xpath)

    def click_flavor_exclusions(self):
        xpath = wtxs.label_button(self.active_cloud, 'flavor-exclusions')
        wti.click_by_xpath(self.driver, xpath)

    def click_flavor_exclusions_checkbox(self, box):
        xpath = wtxs.form_input_by_value(self.active_cloud + '-flavor-exclusions', box)
        wti.click_by_xpath(self.driver, xpath)

    def click_update_flavor_exclusions(self):
        xpath = wtxs.form_submit_by_value(self.active_cloud + '-flavor-exclusions', 'Update Flavor Exclusions')
        wti.click_by_xpath(self.driver, xpath)
 
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

    def metadata_priority_popup_exists(self):
        self.driver.switch_to.frame('editor-' + self.active_cloud + '-' + self.active_metadata)
        popup = wti.get_validation_message_by_name(self.driver, 'priority')
        self.driver.switch_to.default_content()
        if popup:
            return True
        return False

    def cores_popup_exists(self):
        popup = wti.get_validation_message_by_name(self.driver, 'cores_ctl')
        if popup:
            return True
        return False

    def ram_popup_exists(self):
        popup = wti.get_validation_message_by_name(self.driver, 'ram_ctl')
        if popup:
            return True
        return False

class AliasesPage(Page):
    """This is the page object class for the Aliases page."""
    def __init__(self, driver):
        super(AliasesPage, self).__init__(driver)
        # The active_alias variable stores the currently-selected user in the
        # sidebar.
        self.active_alias = None
   
    def click_side_button(self, name):
        wti.click_by_link_text(self.driver, name)
        self.active_alias = name

    def click_add_button(self):
        wti.click_by_link_text(self.driver, '+')
        self.active_alias = 'add_alias'

    def type_alias_name(self, name):
        wti.fill_blank_by_id(self.driver, 'new_alias', name)

    def click_cloud_checkbox(self, box):
        xpath = wtxs.form_input_by_value(self.active_alias, box)
        wti.click_by_xpath(self.driver, xpath)

    def click_add_alias(self):
        xpath = wtxs.form_submit_by_value('add_alias', 'Add')
        wti.click_by_xpath(self.driver, xpath)

    def click_update_alias(self):
        xpath = wtxs.form_submit_by_value(self.active_alias, 'Update')
        wti.click_by_xpath(self.driver, xpath)

    def side_button_exists(self, name):
        sleep(2)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, name)))
            return True
        except TimeoutException:
            return False

class DefaultsPage(Page):
    """This is the page object class for the Defaults page."""
    def __init__(self, driver):
        super(DefaultsPage, self).__init__(driver)
        # The active_cloud variable stores the currently-selected cloud in the
        # sidebar.
        self.active_group = None
        self.active_metadata = None
    
    def click_side_button(self, name):
        wti.click_by_link_text(self.driver, name)
        self.active_group = name
        self.active_metadata = None

    def click_side_tab(self, name):
        element_name = name.lower()
        xpath = wtxs.label_button('defaults', element_name)
        wti.click_by_xpath(self.driver, xpath)
        self.active_metadata = None

    def type_htcondor_fqdn(self, fqdn):
        xpath = wtxs.form_input_by_name(self.active_group, 'htcondor_fqdn')
        wti.fill_blank_by_xpath(self.driver, xpath, fqdn)

    def type_htcondor_container_hostname(self, hostname):
        xpath = wtxs.form_input_by_name(self.active_group, 'htcondor_container_hostname')
        wti.fill_blank_by_xpath(self.driver, xpath, hostname)

    def type_htcondor_other_submitters(self, submitters):
        xpath = wtxs.form_input_by_name(self.active_group, 'htcondor_other_submitters')
        wti.fill_blank_by_xpath(self.driver, xpath, submitters)

    def type_job_cpus(self, cpus):
        xpath = wtxs.form_input_by_name(self.active_group, 'job_cpus')
        wti.fill_blank_by_xpath(self.driver, xpath, cpus)

    def type_job_ram(self, ram):
        xpath = wtxs.form_input_by_name(self.active_group, 'job_ram')
        wti.fill_blank_by_xpath(self.driver, xpath, ram)

    def type_job_disk(self, disk):
        xpath = wtxs.form_input_by_name(self.active_group, 'job_disk')
        wti.fill_blank_by_xpath(self.driver, xpath, disk)

    def type_job_swap(self, swap):
        xpath = wtxs.form_input_by_name(self.active_group, 'job_swap')
        wti.fill_blank_by_xpath(self.driver, xpath, swap) 

    def select_vm_keyname(self, keyname):
        xpath = wtxs.form_select_by_name(self.active_group, 'vm_keyname')
        wti.select_option_by_xpath(self.driver, xpath, keyname)

    def select_vm_image(self, image):
        xpath = wtxs.form_select_by_name(self.active_group, 'vm_image')
        wti.select_option_by_xpath(self.driver, xpath, image)

    def select_vm_flavor(self, flavor):
        xpath = wtxs.form_select_by_name(self.active_group, 'vm_flavor')
        wti.select_option_by_xpath(self.driver, xpath, flavor)

    def select_vm_network(self, network):
        xpath = wtxs.form_select_by_name(self.active_group, 'vm_network')
        wti.select_option_by_xpath(self.driver, xpath, network)

    def type_vm_keep_alive(self, time):
        xpath = wtxs.form_input_by_name(self.active_group, 'vm_keep_alive')
        wti.fill_blank_by_xpath(self.driver, xpath, time)

    def click_update_group(self):
        xpath = wtxs.form_submit_by_value(self.active_group, 'Update Group')
        wti.click_by_xpath(self.driver, xpath)

    def click_metadata_new(self):
        xpath = wtxs.label_button_no_category('metadata-add')
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.frame('editor-add')
        self.active_metadata = 'add'

    def click_metadata(self, name):
        xpath = wtxs.label_button_no_category('metadata-' + name)
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.frame('editor-' + self.active_group + '-'  + name)
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
        xpath = wtxs.form_input_by_value('metadata-form', 'Add')
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.default_content()
        if self.metadata_tab_exists(text):
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

    def click_metadata_delete_cancel(self):
        xpath = wtxs.delete_cancel('metadata')
        wti.click_by_xpath(self.driver, xpath)
        self.driver.switch_to.default_content()

    def side_button_exists(self, name):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, name)))
            return True
        except TimeoutException:
            return False

    def metadata_tab_exists(self, name):
        sleep(2)
        xpath = wtxs.label_button_no_category('metadata-' + name)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

    def metadata_priority_popup_exists(self):
        if self.active_metadata == 'add':
            self.driver.switch_to.frame('editor-' + self.active_metadata)
        else:
            self.driver.switch_to.frame('editor-' + self.active_group + '-' + self.active_metadata)
        popup = wti.get_validation_message_by_name(self.driver, 'priority')
        self.driver.switch_to.default_content()
        if popup:
            return True
        return False

class ImagesPage(Page):
    """This is the page object class for the Images page."""
    def __init__(self, driver):
        super(ImagesPage, self).__init__(driver)
        # There is no active image, so there is no variable for it

    def type_in_search_bar(self, text):
        wti.fill_blank_by_id(self.driver, 'image_search', text)

    def click_upload_image(self):
        xpath = wtxs.input_by_value('+Upload Image')
        wti.click_by_xpath(self.driver, xpath)

    def click_from_url(self):
        xpath = wtxs.button_by_visible_text('From URL')
        wti.click_by_xpath(self.driver, xpath)

    def click_from_file(self):
        xpath = wtxs.button_by_visible_text('From File')
        wti.click_by_xpath(self.driver, xpath)

    def type_image_file_path(self, path):
        wti.fill_blank_by_name(self.driver, 'myfile', path)

    def type_image_url(self, url):
        wti.fill_blank_by_name(self.driver, 'myfileurl', url)

    def select_disk_format(self, format):
        wti.select_option_by_name(self.driver, 'disk_format', format)

    def add_upload_to_cloud(self, cloud):
        wti.select_option_by_id(self.driver, 'rightValues', cloud)
        wti.click_by_id(self.driver, 'btnLeft')

    def remove_upload_to_cloud(self, cloud):
        wti.select_option_by_id(self.driver, 'leftValues', cloud)
        wti.click_by_id(self.driver, 'btnRight')

    def click_cancel_upload(self):
        xpath = wtxs.input_by_value('Cancel')
        wti.click_by_xpath(self.driver, xpath)

    def click_upload(self):
        xpath = wtxs.button_by_visible_text('Upload')
        wti.click_by_xpath(self.driver, xpath)

    def click_download_image(self, image):
        xpath = wtxs.download_button(image)
        wti.click_by_xpath(self.driver, xpath)

    def click_download_ok(self):
        alert = self.driver.switch_to.alert
        alert.accept()

    def click_download_cancel(self):
        alert = self.driver.switch_to.alert
        alert.dismiss()

    def click_cloud_button(self, image, cloud):
        xpath = wtxs.image_cloud_button(image)
        buttons = self.driver.find_elements_by_xpath(xpath)
        cloud_button = None
        for button in buttons:
            text = button.get_attribute('onclick')
            if cloud in text:
                cloud_button = button
        cloud_button.click()

    def click_delete_ok(self):
        alert = self.driver.switch_to.alert
        alert.accept()

    def click_delete_cancel(self):
        alert = self.driver.switch_to.alert
        alert.dismiss()

    def find_non_matching_image(self, pattern):
        images = self.driver.find_elements_by_tag_name('b')
        for image in images:
            text = image.text
            if pattern not in text:
                return text
        return None

    def image_exists(self, image):
        xpath = wtxs.table_row_name('image_row', image)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            elements = self.driver.find_elements_by_xpath(xpath)
            for element in elements:
                if element.is_displayed():
                    return True
            return False
        except TimeoutException:
            return False

    def image_is_public_in_cloud(self, image, cloud):
        sleep(5)
        xpath = wtxs.image_state_box_button(image, 'public')
        elements = self.driver.find_elements_by_xpath(xpath)
        button = None
        for element in elements:
            text = element.get_attribute('onclick')
            if cloud in text:
                button = element
        if button:
            return True
        else:
            return False

    def image_is_private_in_cloud(self, image, cloud):
        sleep(5)
        xpath = wtxs.image_state_box_button(image, 'shared')
        elements = self.driver.find_elements_by_xpath(xpath)
        button = None
        for element in elements:
            text = element.get_attribute('onclick')
            if cloud in text:
                button = element
        if button:
            return True
        else:
            return False

    def image_is_error_in_cloud(self, image, cloud):
        sleep(5)
        xpath = wtxs.image_state_box_button(image, 'error') # TODO: check this
        elements = self.driver.find_elements_by_xpath(xpath)
        button = None
        for element in elements:
            text = element.get_attribute('onclick')
            if cloud in text:
                button = element
        if button:
            return True
        else:
            return False

    def image_is_disabled_in_cloud(self, image, cloud):
        sleep(5)
        xpath = wtxs.image_state_box_button(image, 'missing')
        elements = self.driver.find_elements_by_xpath(xpath)
        button = None
        for element in elements:
            text = element.get_attribute('onclick')
            if cloud in text:
                button = element
        if button:
            return True
        else:
            return False

class KeysPage(Page):
    """This is the page object class for the Keys page."""
    def __init__(self, driver):
        super(KeysPage, self).__init__(driver)
        # There is no active key, so there is no variable here
        # Instead, there is a variable to save whether the popup is an upload
        # or create popup
        self.active_popup = None

    def search_keys(self, key):
        wti.fill_blank_by_id(self.driver, 'image_search')

    def click_upload_key(self):
        wti.click_by_id(self.driver, 'popover-uploadkey')
        self.active_popup = 'upload_key'

    def click_create_key(self):
        wti.click_by_id(self.driver, 'popover-newkey')
        self.active_popup = 'new_key'

    def type_key_name(self, name):
        xpath = wtxs.form_input_by_name(self.active_popup, 'key_name')
        wti.fill_blank_by_xpath(self.driver, xpath, name)

    def type_public_key(self, key):
        xpath = wtxs.form_input_by_name(self.active_popup, 'key_string')
        wti.fill_blank_by_xpath(self.driver, xpath, key)

    def add_upload_to_cloud(self, cloud):
        button_suffix = ''
        select_suffix = ''
        if self.active_popup == 'upload_key':
            button_suffix = 'Upload'
            select_suffix = 'Upload'
        if self.active_popup == 'new_key':
            button_suffix = ''
            select_suffix = 'Create'
        wti.select_option_by_id(self.driver, 'rightValues' + select_suffix, cloud)
        wti.click_by_id(self.driver, 'btnLeft' + button_suffix)

    def remove_to_from_cloud(self, cloud):
        button_suffix = ''
        select_suffix = ''
        if self.active_popup == 'upload_key':
            button_suffix = 'Upload'
            select_suffix = 'Upload'
        if self.active_popup == 'new_key':
            button_suffix = ''
            select_suffix = 'Create'
        wti.select_option_by_id(self.driver, 'leftValues' + select_suffix, cloud)
        wti.click_by_id(self.driver, 'btnRight' + button_suffix)

    def click_submit(self):
        xpath = wtxs.form_submit_by_value(self.active_popup, 'Submit')
        wti.click_by_xpath(self.driver, xpath)
        self.active_popup = None

    def click_submit_changes(self):
        xpath = wtxs.input_by_value('Submit Changes')
        wti.click_by_xpath(self.driver, xpath)

    def click_cloud_checkbox(self, key, cloud):
        checkboxes = self.driver.find_elements_by_name(cloud)
        cloud_checkbox = None
        for box in checkboxes:
            value = box.get_attribute('value')
            if key in value:
                cloud_checkbox = box
        cloud_checkbox.click()

    def key_exists(self, key):
        xpath = wtxs.key_label(key)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

    def cloud_box_checked(self, key, cloud):
        checkboxes = self.driver.find_elements_by_name(cloud)
        cloud_checkbox = None
        for box in checkboxes:
            value = box.get_attribute('value')
            if key in value:
                cloud_checkbox = box
        if cloud_checkbox:
            if cloud_checkbox.is_selected():
                return True
        return False

    def key_error_message_displayed(self, message=None):
        xpath = ''
        if message:
            xpath = wtxs.specific_glint_error_message(message)
        else:
            xpath = wtxs.unspecified_glint_error_message()
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

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
        xpath = wtxs.form_submit_by_value('add_user', 'Add user')
        wti.click_by_xpath(self.driver, xpath)
        self.active_user = text

    def click_side_button(self, name):
        # This method uses the JavaScript click to avoid a Selenium bug with
        # clicking an element when another element's padding covers it.
        wtjsi.javascript_click_by_link_text(self.driver, name)
        self.active_user = name

    def type_username(self, name):
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
        xpath = wtxs.form_submit_by_value(self.active_user, 'Update user')
        wti.click_by_xpath(self.driver, xpath)

    def click_delete_button(self):
        wtjsi.javascript_click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_user, self.active_user)
        wti.click_by_xpath(self.driver, xpath)
        self.active_user = None

    def click_delete_cancel(self):
        xpath = wtxs.delete_cancel(self.active_user)
        wti.click_by_xpath(self.driver, xpath)
    
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
        xpath = wtxs.form_submit_by_value('add_group', 'Add Group')
        wti.click_by_xpath(self.driver, xpath)
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
        xpath = wtxs.form_submit_by_value(self.active_group, 'Update Group')
        wti.click_by_xpath(self.driver, xpath)

    def click_delete_button(self):
        wtjsi.javascript_click_by_link_text(self.driver, '−')

    def click_delete_modal(self):
        xpath = wtxs.delete_button(self.active_group, self.active_group)
        wti.click_by_xpath(self.driver, xpath)
        self.active_group = None

    def click_delete_cancel(self):
        xpath = wtxs.delete_cancel(self.active_group)
        wti.click_by_xpath(self.driver, xpath)

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
    
    def __init__(self, driver):
        super(ConfigPage, self).__init__(driver)
        # The active_config variable stores the active config file in the sidebar
        self.active_config = None

    def click_side_button(self, name):
        # This method uses the JavaScript click to avoid a Selenium bug with
        # clicking an element when another element's padding covers it.
        wtjsi.javascript_click_by_link_text(self.driver, name)
        self.active_config = name

    # Note: these fields are listed in alphabetical order. Not every config file
    # will have every field, and not every config file will necessarily be
    # listed here.
    # Currently, the config files that are fully documented are:
    # condor_poller.py

    def get_value_batch_commit_size(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'batch_commit_size')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_batch_commit_size(self, size):
        xpath = wtxs.div_input_by_name(self.active_config, 'batch_commit_size')
        wti.fill_blank_by_xpath(self.driver, xpath, size)

    def get_value_ca_certs(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'cacerts')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_ca_certs(self, ca_certs):
        xpath = wtxs.div_input_by_name(self.active_config, 'cacerts')
        wti.fill_blank_by_xpath(self.driver, xpath, ca_certs)

    def get_value_delete_cycle_interval(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'delete_cycle_interval')
        element = self.driver.find_element_by_xpath(xpath)
        text = element.get_attribute('value')
        return text

    def type_delete_cycle_interval(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'delete_cycle_interval')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def get_value_log_file(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'log_file')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_log_file(self, file):
        xpath = wtxs.div_input_by_name(self.active_config, 'log_file')
        wti.fill_blank_by_xpath(self.driver, xpath, file)

    def get_text_log_level(self):
        xpath = wtxs.div_select_by_name(self.active_config, 'log_level')
        xpath += "/option[@selected='']"
        element = self.driver.find_element_by_xpath(xpath)
        text = element.text
        return text

    def select_log_level(self, level):
        xpath = wtxs.div_select_by_name(self.active_config, 'log_level')
        wti.select_option_by_xpath(self.driver, xpath, level)

    def get_value_retire_interval(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'retire_interval')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_retire_interval(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'retire_interval')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def click_retire_off(self):
        xpath = wtxs.div_input_by_name_not_hidden(self.active_config, 'retire_off')
        wti.click_by_xpath(self.driver, xpath)

    def get_value_sleep_interval_command(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_command')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_sleep_interval_command(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_command')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def get_value_sleep_interval_condor_gsi(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_condor_gsi')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_sleep_interval_condor_gsi(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_condor_gsi')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def get_value_sleep_interval_job(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_job')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_sleep_interval_job(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_job')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def get_value_sleep_interval_machine(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_machine')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_sleep_interval_machine(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_machine')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def get_value_sleep_interval_worker_gsi(self):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_worker_gsi')
        element = self.driver.find_element_by_xpath(xpath)
        value = element.get_attribute('value')
        return value

    def type_sleep_interval_worker_gsi(self, interval):
        xpath = wtxs.div_input_by_name(self.active_config, 'sleep_interval_worker_gsi')
        wti.fill_blank_by_xpath(self.driver, xpath, interval)

    def click_update_config(self):
        xpath = wtxs.div_submit_by_value(self.active_config, 'Update Config')
        wti.click_by_xpath(self.driver, xpath)

class SettingsPage(Page):
    """This is the page object class for the User Settings page."""
    
    def __init__(self, driver):
        super(SettingsPage, self).__init__(driver)
        # The active_user variable stores the active user in the sidebar
        self.active_user = None

    def click_side_button(self, name):
        wti.click_by_link_text(self.driver, name)
        self.active_user = name

    def type_password(self, password, alt_password=None):
        if not alt_password:
            alt_password = password
        xpath1 = wtxs.form_input_by_name_not_hidden(self.active_user, 'password1')
        xpath2 = wtxs.form_input_by_name_not_hidden(self.active_user, 'password2')
        wti.fill_blank_by_xpath(self.driver, xpath1, password)
        wti.fill_blank_by_xpath(self.driver, xpath2, alt_password)

    def click_global_view_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'flag_global_status')
        wti.click_by_xpath(self.driver, xpath)

    def click_jobs_by_alias_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'flag_jobs_by_target_alias')
        wti.click_by_xpath(self.driver, xpath)

    def click_foreign_global_vms_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'flag_show_foreign_global_vms')
        wti.click_by_xpath(self.driver, xpath)

    def click_slot_detail_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'flag_show_slot_detail')
        wti.click_by_xpath(self.driver, xpath)

    def click_slot_flavor_info_checkbox(self):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'flag_show_slot_flavors')
        wti.click_by_xpath(self.driver, xpath)

    def type_status_refresh(self, refresh):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'status_refresh_interval')
        wti.fill_blank_by_xpath(self.driver, xpath, refresh)

    def increment_status_refresh_by_arrows(self, refresh):
        xpath = wtxs.form_input_by_name_not_hidden(self.active_user, 'status_refresh_interval')
        element = self.driver.find_element_by_xpath(xpath)
        start = int(element.get_attribute('value'))
        if start < refresh:
            for i in range(start, refresh):
                element.send_keys(Keys.ARROW_UP)
        else:
            for i in range(refresh, start):
                element.send_keys(Keys.ARROW_DOWN)

    def select_default_group(self, group):
        xpath = wtxs.form_select_by_name(self.active_user, 'default_group')
        wti.select_option_by_xpath(self.driver, xpath, group)

    def click_update_user(self):
        xpath = wtxs.form_input_by_value(self.active_user, 'Update user')
        wti.click_by_xpath(self.driver, xpath)

    def status_refresh_popup_exists(self):
        popup = wti.get_validation_message_by_name(self.driver, 'status_refresh_interval')
        if popup:
            return True
        return False
