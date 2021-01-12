from behave import fixture, use_fixture
from selenium import webdriver

@fixture
def after_scenario(context, scenario):
    context.driver.quit()
