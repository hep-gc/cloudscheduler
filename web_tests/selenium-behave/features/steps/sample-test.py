from behave import *
#from selenium import webdriver

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
    #TODO
    pass

@when('we navigate to Google')
def step_impl(context):
    #TODO
    pass

@then('there should be a search bar')
def step_impl(context):
    #TODO
    assert True is True

@given('we are on Google')
def step_impl(context):
    #TODO
    pass

@when('we try to type in the search bar')
def step_impl(context):
    #TODO
    pass

@then('we should be successful')
def step_impl(context):
    #TODO
    assert True is True

@when('we type in the search bar')
def step_impl(context):
    #TODO
    pass

@when('search')
def step_impl(context):
    #TODO
    pass
