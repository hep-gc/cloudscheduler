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

def div_input_by_value(div, value):
    return "//div[@id='" + div + "']//input[@value='" + value + "']"

def div_input_by_name(div, name):
    return "//div[@id='" + div + "']//input[@name='" + name + "']"

def div_input_by_name_not_hidden(div, name):
    return "//div[@id='" + div + "']//input[@name='" + name + "' and not(@type='hidden')]"

def div_select_by_name(div, name):
    return "//div[@id='" + div + "']//select[@name='" + name + "']"

def div_select_by_value(div, value):
    return "//div[@id='" + div + "']//select[@value='" + value + "']"

def div_submit_by_value(div, value):
    return "//div[@id='" + div + "']//input[@value='" + value + "']"

def button_by_visible_text(text):
    return "//button[contains(text(), '" + text + "')]"

def button_by_value(value):
    return "//button[@value='" + value + "']"

def input_by_value(value):
    return "//input[@value='" + value + "']"

def table_row_name(cls, row):
    return "//tr[@class='" + cls + "']//b[contains(text(), '" + row + "')]"

def table_row_name_not_hidden(cls, row):
    return "//tr[@class='" + cls + "' and not contains(@style, 'display: none')]//b[contains(text(), '" + row + "')]"

def label_button(element, button):
    return "//label[@for='" + element + "-" + button + "']"

def label_button_no_category(button):
    return "//label[@for='" + button + "']"

def download_button(image_name):
    return "//b[contains(text(), '" + image_name + "')]/following-sibling::img[@title='Download Image']"

def image_cloud_button(image_name):
    return "//b[contains(text(), '" + image_name + "')]/../..//button[@title='Delete image']"

def image_state_box_button(image_name, state):
    return "//b[contains(text(), '" + image_name + "')]/../..//td[@class='" + state + "']/button[@title='Delete image']"

def key_label(key_name):
    return "//th[contains(text(), '" + key_name + "')]"

def delete_button(item_name, element_name):
    return "//div[@id='delete-" + item_name + "']//input[@value='Delete "+ element_name + "']"

def delete_cancel(item_name):
    return "//div[@id='delete-" + item_name + "']//a[@title='Close']"

def unspecified_error_message():
    return "//div[@class='footer']/b"

def specific_error_message(message):
    return "//div[@class='footer']/b[contains(text(), '" + message + "')]"

def unspecified_glint_error_message():
    return "//h3[@style='color:red']"

def specific_glint_error_message(message):
    return "//h3[@style='color:red' and contains(text(), '" + message + "')]"
