from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def get_homepage(driver):
    driver.get("https://csv2-dev.heprc.uvic.ca")

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
    #form.send_keys(Keys.ENTER)

def click_menu_button(driver, id):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, id)))
    button = driver.find_element_by_id(id)
    button.click()

def click_by_value(driver, name, text):
    #xpath = "//div[@id='" + name + "']/div/form/table/tbody/tr/td/input[@value='" + text + "']"
    #xpath = "//form[@name='" + name + "']/table/tbody/tr/td/input[@value='" + text + "']"
    xpath = "//form[@name='" + name + "']/table/tbody/tr/td/input[@value='" + text + "']"

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    box = driver.find_element_by_xpath(xpath)
    box.click()
