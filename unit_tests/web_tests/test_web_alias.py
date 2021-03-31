import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
import web_tests.web_test_helpers as helpers

class TestWebAliasCommon(unittest.TestCase):
    """A class for the alias tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.AliasesPage(cls.driver)
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        helpers.get_homepage(self.driver)
        self.page.click_top_nav('Aliases')

    def test_web_alias_add(self):
        # Adds an alias
        alias_name = self.gvar['user'] + '-wia4'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_add_alias()
        self.assertTrue(self.page.side_button_exists(alias_name))
        wta.assertExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_without_name(self):
        # Tries to add an alias without a name
        self.page.click_add_button()
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_alias_add_with_conflicting_name(self):
        # Tries to add an alias with a name that's already taken
        alias_name = self.gvar['user'] + '-wia1'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('alias', alias_name, 'clouds', cloud_name, group=self.gvar['base_group'], name_field=False)

    def test_web_alias_add_name_with_symbols(self):
        # Tries to add an alias with symbols in its name
        alias_name = 'inv@|id-web-te$t'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_name_with_two_dashes(self):
        # Tries to add an alias with double dashes in its name
        alias_name = 'invalid--web--test'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_name_with_uppercase(self):
        # Tries to add an alias with uppercase letters in its name
        alias_name = 'INVALID-WEB-TEST'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_name_with_starting_ending_dash(self):
        # Tries to add an alias with starting and ending dashes in its name
        alias_name = '-invalid-web-test-'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_name_too_long(self):
        # Tries to add an alias with a name that's too long for the database
        alias_name = self.oversize['varchar_32']
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_add_without_cloud(self):
        # Tries to add an alias with no clouds in it
        alias_name = self.gvar['user'] + '-wia5'
        self.page.click_add_button()
        self.page.type_alias_name(alias_name)
        self.page.click_add_alias()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    @unittest.skip("Not working in production")
    def test_web_alias_delete(self):
        # Deletes an alias
        alias_name = self.gvar['user'] + '-wia3'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(self.gvar['user'] + '-wic1')
        self.page.click_update_alias()
        self.assertFalse(self.page.side_button_exists(alias_name))
        wta.assertNotExists('alias', alias_name, self.gvar['base_group'])

    def test_web_alias_find(self):
        # Finds the aliases page
        pass

    def test_web_alias_update_cloud_add(self):
        # Adds a cloud to an alias
        alias_name = self.gvar['user'] + '-wia1'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_update_alias()
        wta.assertHasAttribute('alias', alias_name, 'clouds', cloud_name, group=self.gvar['base_group'], name_field=False)

    def test_web_alias_update_cloud_remove(self):
        # Removes a cloud from an alias
        alias_name = self.gvar['user'] + '-wia2'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(alias_name)
        self.page.click_cloud_checkbox(cloud_name)
        self.page.click_update_alias()
        wta.assertHasNotAttribute('alias', alias_name, 'clouds', cloud_name, group=self.gvar['base_group'], name_field=False)

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebAliasSuperUserFirefox(TestWebAliasCommon):
    """A class to test alias operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['aliases'], browser='firefox')
        super(TestWebAliasSuperUserFirefox, cls).setUpClass()
        print("\nAlias Tests (Super User):")

class TestWebAliasRegularUserFirefox(TestWebAliasCommon):
    """A class to test alias operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['aliases'])
        super(TestWebAliasRegularUserFirefox, cls).setUpClass()
        print("\nAlias Tests (Regular User):")

class TestWebAliasSuperUserChromium(TestWebAliasCommon):
    """A class to test alias operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['aliases'], browser='chromium')
        super(TestWebAliasSuperUserChromium, cls).setUpClass()
        print("\nAlias Tests (Chromium) (Super User):")

class TestWebAliasRegularUserChromium(TestWebAliasCommon):
    """A class to test alias operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['aliases'], browser='chromium')
        super(TestWebAliasRegularUserChromium, cls).setUpClass()
        print("\nAlias Tests (Chromium) (Regular User):")

class TestWebAliasSuperUserOpera(TestWebAliasCommon):
    """A class to test alias operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['aliases'], browser='opera')
        super(TestWebAliasSuperUserOpera, cls).setUpClass()
        print("\nAlias Tests (Opera) (Super User):")

class TestWebAliasRegularUserOpera(TestWebAliasCommon):
    """A class to test alias operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['aliases'], browser='opera')
        super(TestWebAliasRegularUserOpera, cls).setUpClass()
        print("\nAlias Tests (Opera) (Regular User):")

if __name__ == '__main__':
    unittest.main()
