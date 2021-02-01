from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# This module contains a variety of interactions (mainly clicks and text fills)
# that can be used to interact with a page. These functions wrap the wait to
# ensure the object exists, the locating of the element, and the action on the
# element into one function.

def click_by_link_text(driver, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text)))
    nav_button = driver.find_element_by_link_text(text)
    nav_button.click()

def click_by_id(driver, id):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, id)))
    button = driver.find_element_by_id(id)
    button.click()

def click_by_xpath(driver, xpath):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    element = driver.find_element_by_xpath(xpath)
    element.click()

def fill_blank_by_id(driver, id, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, id)))
    form = driver.find_element_by_id(id)
    form.clear()
    form.send_keys(text)

def fill_blank_by_name(driver, name, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.NAME, name)))
    form = driver.find_element_by_name(name)
    form.clear()
    form.send_keys(text)

def fill_blank_by_xpath(driver, xpath, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    form = driver.find_element_by_xpath(xpath)
    form.clear()
    form.send_keys(text)
