import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebGroup(unittest.TestCase):
    """A class to test group operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['groups'])
        cls.page = pages.GroupsPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        print("\nGroup Tests:")
        
    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Groups')

    def test_web_group_find(self):
        # Finds the groups page
        pass

    def test_web_group_add_without_name(self):
        # Tries to add a group without naming it
        user_name = self.gvar['user'] + '-wiu1'
        self.page.click_add_button()
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_group_add_with_conflicting_name(self):
        # Tries to add a group with a name that's already taken
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu3'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_add_without_user(self):
        # Adds a group with no users
        group_name = self.gvar['user'] + '-wig7'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_add_group()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertExists('group', group_name)

    def test_web_group_add_checkbox(self):
        # Adds a group with a user, using the checkbox to select the user
        group_name = self.gvar['user'] + '-wig5'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    @unittest.skip("Not working in production")
    def test_web_group_add_search_bar(self):
        # Adds a group with a user, using the search bar to select the user
        group_name = self.gvar['user'] + '-wig6'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.type_in_search_bar(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_add_name_with_symbols(self):
        # Tries to add a group with symbols in its name
        group_name = 'inv@|id-web-te$t'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(group_name))
        wta.assertNotExists('group', group_name)

    def test_web_group_add_name_with_two_dashes(self):
        # Tries to add a group with two dashes in its name
        group_name = 'invalid--web--test'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(group_name))
        wta.assertNotExists('group', group_name)

    def test_web_group_add_name_with_uppercase(self):
        # Tries to add a group with uppercase letters in its name
        group_name = 'INVALID-WEB-TEST'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(group_name))
        wta.assertNotExists('group', group_name)

    def test_web_group_add_name_with_starting_ending_dash(self):
        # Tries to add a group with starting and ending dashes in its name
        group_name = '-invalid-web-test-'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(group_name))
        wta.assertNotExists('group', group_name)

    def test_web_group_add_name_too_long(self):
        # Tries to add a group with a name too long for the database
        group_name = self.oversize['varchar_32']
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertFalse(self.page.side_button_exists(group_name))
        wta.assertNotExists('group', group_name)

    def test_web_group_delete(self):
        # Deletes a group
        group_name = self.gvar['user'] + '-wig4'
        self.page.click_side_button(group_name)
        self.page.click_delete_button()
        self.page.click_delete_modal()
        self.assertFalse(self.page.side_button_exists(group_name))
        wta.assertNotExists('group', group_name)

    def test_web_group_delete_cancel(self):
        # Tries to delete a group but clicks cancel
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_side_button(group_name)
        self.page.click_delete_button()
        self.page.click_delete_cancel()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertExists('group', group_name)

    @unittest.skip("Not working in production")
    def test_web_group_update_user_add_search_bar(self):
        # Adds a user to a group using the search bar
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_side_button(group_name)
        self.page.type_in_search_bar(user_name)
        self.page.click_update_group()
        self.assertTrue(self.page.box_checked(user_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_update_user_add_checkbox(self):
        # Adds a user to a group using a checkbox
        group_name = self.gvar['user'] + '-wig2'
        user_name = self.gvar['user'] + '-wiu1'
        self.page.click_side_button(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_update_group()
        self.assertTrue(self.page.box_checked(user_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_update_user_remove(self):
        # Removes a user from a group
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu1'
        self.page.click_side_button(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_update_group()
        self.assertFalse(self.page.box_checked(user_name))
        wta.assertHasNotAttribute('user', user_name, 'user_groups', group_name) 

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
