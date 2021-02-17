# This module contains wrapper functions for the xpath paths of various web
# elements for the web tests.

def form_input_by_value(form, value):
    return "//form[@name='" + form + "']//input[@value='" + value + "']"

def form_input_by_name(form, name):
    return "//form[@name='" + form + "']//input[@name='" + name + "']"

def form_input_by_name_not_hidden(form, name):
    return "//form[@name='" + form + "']//input[@name='" + name + "' and not(@type='hidden')]"

def form_select_by_name(form, name):
    return "//form[@name='" + form + "']//select[@name='" + name + "']"

def form_select_by_value(form, value):
    return "//form[@name='" + form + "']//select[@value='" + value + "']"

def form_submit_by_value(form, value):
    return "//form[@name='" + form + "']//input[@value='" + value + "']"

def label_button(element, button):
    return "//label[@for='" + element + "-" + button + "']"

def delete_button(item_name, element_name):
    return "//div[@id='delete-" + item_name + "']/div/form/input[@value='Delete "+ element_name + "']"

def unspecified_error_message():
    return "//div[@class='footer']/b"

def specific_error_message(message):
    return "//div[@class='footer']/b[text()='" + message + "']"
