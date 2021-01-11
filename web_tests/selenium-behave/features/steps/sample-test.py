from behave import *
from selenium import webdriver

@given('we have done the setup correctly')
def step_impl(context):
    pass

@when('we run a simple test')
def step_impl(context):
    assert True is True

@then('it will pass')
def step_impl(context):
    assert context.failed is False

@given('we have our browser set up')
def step_impl(context):
    context.driver = webdriver.Firefox()

@when('we navigate to Google')
def step_impl(context):
    context.driver.get("https://google.com")

@then('there should be a search bar')
def step_impl(context):
    context.driver.find_element_by_name("q")
    assert context.failed is False

@given('we are on Google')
def step_impl(context):
    context.execute_steps(u'when we navigate to Google')

@when('we type in the search bar')
def step_impl(context):
    context.search_bar = context.driver.find_element_by_name("q")
    context.search_bar.send_keys('cloudscheduler')

@then('we should be successful')
def step_impl(context):
    assert context.failed is False

@when('we search')
def step_impl(context):
    context.search_bar.submit()
