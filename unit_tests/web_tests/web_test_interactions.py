from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

# This module contains a variety of interactions (mainly clicks and text fills)
# that can be used to interact with a page. These functions wrap the wait to
# ensure the object exists, the locating of the element, and the action on the
# element into one function.

default_timeout = 20


class wait_for_page_load(object):
    """
    Context for waiting for a new page to be loaded upon the completion
    of (some) actions. This works by checking for the staleness of an
    element on the previous page. Largely based on:
    https://www.cloudbees.com/blog/get-selenium-to-wait-for-page-load.
    """

    def __init__(self, browser, timeout=default_timeout):
        self.browser, self.timeout = browser, timeout

    def __enter__(self):
        self.old_page = self.browser.find_element(By.TAG_NAME, 'html')

    def __exit__(self, *_):
        WebDriverWait(self.browser, self.timeout).until(EC.staleness_of(self.old_page))


def click_by_link_text(driver, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text)))
    nav_button = driver.find_element(By.LINK_TEXT, text)
    nav_button.click()


def click_by_id(driver, id, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, id)))
    button = driver.find_element(By.ID, id)
    button.click()


def click_by_name(driver, name, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, name)))
    element = driver.find_element(By.NAME, name)
    element.click()


def click_by_xpath(driver, xpath, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    element = driver.find_element(By.XPATH, xpath)
    element.click()


def click_by_class_name(driver, class_name, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    element = driver.find_element(By.CLASS_NAME, class_name)
    element.click()


def fill_blank_by_id(driver, id, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, id)))
    form = driver.find_element(By.ID, id)
    form.clear()
    form.send_keys(text)
    if form.get_attribute('value') != text:
        form.clear()
        for letter in text:
            form.send_keys(letter)


def fill_blank_by_name(driver, name, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, name)))
    form = driver.find_element(By.NAME, name)
    form.clear()
    form.send_keys(text)
    if form.get_attribute('value') != text:
        form.clear()
        for letter in text:
            form.send_keys(letter)


def fill_blank_by_xpath(driver, xpath, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    form = driver.find_element(By.XPATH, xpath)
    form.clear()
    form.send_keys(text)
    if form.get_attribute('value') != text:
        form.clear()
        for letter in text:
            form.send_keys(letter)


def fill_blank_by_tag_name(driver, tag_name, text, timeout=default_timeout):
    # Note: only use this method when there is definitely only one element with
    # this tag name.
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, tag_name)))
    form = driver.find_element(By.TAG_NAME, tag_name)
    form.clear()
    form.send_keys(text)
    if form.get_attribute('value') != text:
        form.clear()
        for letter in text:
            form.send_keys(letter)


def select_option_by_id(driver, id, option, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, id)))
    dropdown = Select(driver.find_element(By.ID, id))
    dropdown.select_by_visible_text(option)


def select_option_by_name(driver, name, option, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, name)))
    dropdown = Select(driver.find_element(By.NAME, name))
    dropdown.select_by_visible_text(option)


def select_option_by_xpath(driver, xpath, option, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    dropdown = Select(driver.find_element(By.XPATH, xpath))
    dropdown.select_by_visible_text(option)


def slide_slider_by_xpath(driver, xpath, offset, vertical_offset, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    slider = driver.find_element(By.XPATH, xpath)
    action = ActionChains(driver).move_to_element_with_offset(slider, offset, vertical_offset).click()
    action.perform()


def right_click_by_xpath(driver, xpath, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    element = driver.find_element(By.XPATH, xpath)
    action = ActionChains(driver).context_click(element)
    action.perform()


def get_validation_message_by_name(driver, name, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.NAME, name)))
    element = driver.find_element(By.NAME, name)
    message = element.get_attribute('validationMessage')
    return message
