# This module contains wrapper functions for the xpath paths of various web
# elements for the web tests.

def checkbox(form_name, box_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/input[@value='" + box_name + "']"

def form_blank(form_name, blank_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/input[@name='" + blank_name + "']"

def dropdown(form_name, dropdown_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/select[@name='" + dropdown_name + "']"

def option_box(form_name, box_value):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/section/div/select[@value='" + box_value + "']"

def two_column_checkbox(form_name, box_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/table/tbody/tr/td/input[@value='" + box_name + "']"

def two_column_form_blank(form_name, blank_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/table/tbody/tr/td/input[@name='" + blank_name + "']"

def two_column_dropdown(form_name, dropdown_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/table/tbody/tr/td/select[@name='" + dropdown_name "']"

def two_column_option_box(form_name, box_value):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/table/tbody/tr/td/section/div/select[@value='" + box_value + "']"

def delete_button(element_name):
    return "//div[@id='delete-" + element_name + "']/div/form/input[@value='Delete "+ element_name + "']"

def unspecified_error_message():
    return "//div[@class='footer']/b"

def specific_error_message(message):
    return "//div[@class='footer']/b[text()='" + message + "']"
