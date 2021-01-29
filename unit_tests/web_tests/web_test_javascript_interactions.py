from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# IMPORTANT: This module contains functions to use JavaScript to override 
# Selenium's view of elements being non-interactable. These functions should not
# be used as a substitute for Selenium's default functions - the functions in 
# web_test_interactions should always be used if possible. These functions 
# should only be used where Selenium errors are preventing interaction with an 
# element the user can interact with (this should be manually tested). Every use
# of these  functions should contain a documented reason why the Selenium 
# functions cannot be used in the comments above the use of these functions

def javascript_click(driver, element):
    # wrapper function for clicking the item via JavaScript
    driver.execute_script("arguments[0].click();", element)

def javascript_click_by_xpath(driver, xpath):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    box = driver.find_element_by_xpath(xpath)
    javascript_click(driver, box)

def javascript_click_by_link_text(driver, text):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.LINK_TEXT, text)))
    button = driver.find_element_by_link_text(text)
    javascript_click(driver, button)
