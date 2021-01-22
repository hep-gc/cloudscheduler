from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def click_nav_button(driver, text):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text)))
    nav_button = driver.find_element_by_link_text(text)
    nav_button.click()
