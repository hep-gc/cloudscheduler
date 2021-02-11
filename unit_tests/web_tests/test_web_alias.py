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
        alias_name = self.gvar['user'] + '-wia4'
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
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttributeNoNameFlag('alias', alias_name, 'clouds', cloud_name, self.gvar['base_group'])


    def test_web_alias_add_without_cloud(self):
        alias_name = self.gvar['user'] + '-wia5'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('alias', alias_name, self.gvar['base_group'])

    @unittest.skip("Not working in production")
    def test_web_alias_delete(self):
        alias_name = self.gvar['user'] + '-wia3'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_update_alias()
        self.assertFalse(self.page.side_button_exists(alias_name))
        wta.assertDeleted('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_find(self):
        pass

    def test_web_alias_update_cloud_add(self):
        alias_name = self.gvar['user'] + '-wia1'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_update_alias()
        wta.assertHasAttributeNoNameFlag('alias', alias_name, 'clouds', cloud_name, self.gvar['base_group'])

    def test_web_alias_update_cloud_remove(self):
        alias_name = self.gvar['user'] + '-wia2'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_update_alias()
        wta.assertHasNotAttributeNoNameFlag('alias', alias_name, 'clouds', cloud_name, self.gvar['base_group'])

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebAliasRegularUser(unittest.TestCase):
    """A class to test alias operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['aliases'])
        cls.page = pages.AliasesPage(cls.driver)
        print("\nAlias Tests (Regular User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Aliases')

    def test_web_alias_add(self):
        alias_name = self.gvar['user'] + '-wia4'
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
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttributeNoNameFlag('alias', alias_name, 'clouds', cloud_name, self.gvar['base_group'])


    def test_web_alias_add_without_cloud(self):
        alias_name = self.gvar['user'] + '-wia5'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('alias', alias_name, self.gvar['base_group'])

    @unittest.skip("Not working in production")
    def test_web_alias_delete(self):
        alias_name = self.gvar['user'] + '-wia3'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_update_alias()
        self.assertFalse(self.page.side_button_exists(alias_name))
        wta.assertDeleted('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_find(self):
        pass

    def test_web_alias_update_cloud_add(self):
        alias_name = self.gvar['user'] + '-wia1'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_update_alias()
        wta.assertHasAttributeNoNameFlag('alias', alias_name, 'clouds', cloud_name, self.gvar['base_group'])

    def test_web_alias_update_cloud_remove(self):
        alias_name = self.gvar['user'] + '-wia2'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_update_alias()
        wta.assertHasNotAttributeNoNameFlag('alias', alias_name, 'clouds', cloud_name, self.gvar['base_group'])

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == '__main__':
    unittest.main()
