from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import unittest
from time import sleep
import web_common as wc

class TestAliases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.load_web_settings('/alias/list/')
        cls.driver = cls.gvar['driver']
        cls.active_group = cls.gvar['user'] + '-wig1'
        cls.alias_to_list = cls.gvar['user'] + '-wia1'
        cls.alias_to_delete = cls.gvar['user'] + '-wia2'
        cls.alias_to_update = cls.gvar['user'] + '-wia2'
        cls.alias_to_add = cls.gvar['user'] + '-wia3'
        cls.cloud_to_list = cls.gvar['user'] + '-wic1'
        # cloud_name.1 == cls.cloud_to_list
        cls.alias_add_mandatory_parameters = {'cloud_name.1': True}
        cls.alias_add_invalid_combinations = {
            'alias_name': {
                '': 'alias add value specified for "alias_name" must not be the empty string.',
                'Invalid-Unit-Test': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'invalid-unit--test': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                '-invalid-unit-test': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'invalid-unit-test!': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'alias-name-that-is-too-long-for-the-database': 'Data too long for column \'alias_name\' at row 1',
                cls.alias_to_list: 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(cls.active_group, cls.alias_to_list)
            }
        }

    def test_nav(self):
        wc.assert_nav(self.driver, self.fail, self.gvar['address'])

    def test_alias_add(self):
        listing_xpath = '//*[contains(@class, "menu")]//*[@id="add-alias"]'
        form_xpath = listing_xpath + '//form[@name="add_alias"]'
        link_xpath = listing_xpath + '//a[text()="+"]'
        wc.submit_invalid_combinations(self.driver, self.fail, form_xpath, self.alias_add_invalid_combinations, self.alias_add_mandatory_parameters, self.gvar['max_wait'], click_before_filling=link_xpath)
        wc.assert_one(self.driver, self.fail, (By.XPATH, link_xpath)).click()
        valid_combination = {**self.alias_add_mandatory_parameters, 'alias_name': self.alias_to_add}
        wc.submit_form(self.driver, self.fail, form_xpath, valid_combination, expected_response='cloud alias "{}.{}" successfully added.'.format(self.active_group, self.alias_to_add))

    @unittest.skip
    def test_alias_delete(self):
        raise NotImplementedError()

    def test_alias_update(self):
        self.select_alias(self.alias_to_update)
        form_xpath = '//*[contains(@class, "menu")]//*[@id="{0}"]//form[@name="{0}"]'.format(self.alias_to_update)
        # 'cloud_name.3' represents the cloud_to_update.
        wc.submit_form(self.driver, self.fail, form_xpath, {'cloud_name.3': True}, expected_response='cloud alias "{}.{}" successfully updated.'.format(self.active_group, self.alias_to_update), retains_values=True)

    def select_alias(self, alias_name=None):
        if alias_name:
            alias_listing = wc.assert_one(self.driver, self.fail, (By.XPATH, '//*[contains(@class, "menu")]//*[@id="{}"]'.format(alias_name)))
            wc.assert_one(alias_listing, self.fail, (By.LINK_TEXT, alias_name)).click()
            return wc.assert_one(alias_listing, self.fail, (By.TAG_NAME, 'form'), {'name': alias_name})
        # Click the link to add an alias.
        else:
            add_listing = wc.assert_one(self.driver, self.fail, (By.XPATH, '//*[contains(@class, "menu")]//*[@id="add-alias"]'))
            wc.assert_one(add_listing, self.fail, (By.LINK_TEXT, '+')).click()
            return wc.assert_one(alias_listing, self.fail, (By.TAG_NAME, 'form'), {'name': 'add_alias'})

    @classmethod
    def tearDownClass(cls):
        cls.gvar['driver'].quit()

if __name__ == '__main__':
    unittest.main()
