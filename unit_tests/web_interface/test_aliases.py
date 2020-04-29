from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import unittest
from time import sleep
import web_common as wc

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.load_web_settings('/cloud/status/')
        cls.driver = cls.gvar['driver']
        cls.alias_to_list = cls.gvar['user'] + '-wia1'
        cls.alias_to_delete = cls.alias_to_update = cls.gvar['user'] + '-wia2'
        cls.alias_to_add = cls.gvar['user'] + '-wia3'

    def test_nav(self):
        wc.assert_nav(self.driver, self.fail, self.gvar['address'])

    def test_alias_update(self):
        pass

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
