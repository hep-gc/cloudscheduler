from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def click_nav_button(driver, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text)))
    nav_button = driver.find_element_by_link_text(text)
    nav_button.click()

def fill_blank(driver, id, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, id)))
    form = driver.find_element_by_id(id)
    form.clear()
    form.send_keys(text)

def click_by_value(driver, text):
    xpath = "//form[input/@value='" + text + "']"
    #WebDriverWait(driver, 20).until(
    #    EC.element_to_be_clickable((By.XPATH, xpath)))
    box = driver.find_element_by_xpath(xpath)
    box.click()

def javascript_click(driver, element):
    # wrapper function for clicking the item via JavaScript
    driver.execute_script("arguments[0].click();", element)
