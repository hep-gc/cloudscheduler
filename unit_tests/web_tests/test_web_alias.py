import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions as wta
import web_tests.web_test_page_objects as pages

class TestWebAliasSuperUser(unittest.TestCase):
    """A class to test alias operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['aliases'])
        cls.page = pages.AliasesPage(cls.driver)
        print("\nAlias Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Aliases')

    def test_web_alias_add(self):
        alias_name = self.gvar['user'] + '-wia3'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_add_alias()
        self.assertTrue(self.page.side_button_exists(alias_name))
        wta.assertAdded('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_without_name(self):
        self.page.click_add_button()
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_alias_add_with_conflicting_name(self):
        alias_name = self.gvar['user'] + '-wia1'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic2')
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_alias_add_without_cloud(self):
        alias_name = self.gvar['user'] + '-wia4'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_find(self):
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)
