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

def click_by_link_text(driver, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text)))
    nav_button = driver.find_element_by_link_text(text)
    nav_button.click()

def click_by_id(driver, id, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, id)))
    button = driver.find_element_by_id(id)
    button.click()

def click_by_name(driver, name, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, name)))
    element = driver.find_element_by_name(name)
    element.click()

def click_by_xpath(driver, xpath, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    element = driver.find_element_by_xpath(xpath)
    element.click()

def fill_blank_by_id(driver, id, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, id)))
    form = driver.find_element_by_id(id)
    form.clear()
    form.send_keys(text)

def fill_blank_by_name(driver, name, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, name)))
    form = driver.find_element_by_name(name)
    form.clear()
    form.send_keys(text)

def fill_blank_by_xpath(driver, xpath, text, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    form = driver.find_element_by_xpath(xpath)
    form.clear()
    form.send_keys(text)

def fill_blank_by_tag_name(driver, tag_name, text, timeout=default_timeout):
    # Note: only use this method when there is definitely only one element with
    # this tag name.
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, tag_name)))
    form = driver.find_element_by_tag_name(tag_name)
    form.clear()
    form.send_keys(text)

def select_option_by_id(driver, id, option, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, id)))
    dropdown = Select(driver.find_element_by_id(id))
    dropdown.select_by_visible_text(option)

def select_option_by_name(driver, name, option, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, name)))
    dropdown = Select(driver.find_element_by_name(name))
    dropdown.select_by_visible_text(option)

def select_option_by_xpath(driver, xpath, option, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    dropdown = Select(driver.find_element_by_xpath(xpath))
    dropdown.select_by_visible_text(option)

def slide_slider_by_xpath(driver, xpath, offset, vertical_offset, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    slider = driver.find_element_by_xpath(xpath)
    action = ActionChains(driver).move_to_element_with_offset(slider, offset, vertical_offset).click()
    action.perform()

def get_validation_message_by_name(driver, name, timeout=default_timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.NAME, name)))
    element = driver.find_element_by_name(name)
    message = element.get_attribute('validationMessage')
    return message
