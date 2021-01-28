#TODO: investigate page objects for doing this

def user_checkbox(form_name, box_name):
    return "//form[@name='" + form_name + "']/table/tbody/tr/td/input[@value='" + box_name + "']"

def delete_button(element_name):
    return "//div[@id='delete-" + element_name + "']/div/form/input[@value='Delete "+ element_name + "']"
