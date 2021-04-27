if __name__ == "__main__":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebUserCommon(unittest.TestCase):
    """A class for the user tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.UsersPage(cls.driver, cls.gvar['address'])
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        helpers.get_homepage()
        self.page.click_top_nav('Users')

    def test_web_user_find(self):
        # Finds the users page
        pass

    def test_web_user_add_with_group(self):
        # Adds a user who's in a group
        username = self.gvar['user'] + '-wiu5'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(username))
        self.assertTrue(self.page.group_box_checked(group_name))
        wta.assertHasAttribute('user', username, 'user_groups', group_name)

    def test_web_user_add_without_group(self):
        # Adds a user who's not in any groups
        username = self.gvar['user'] + '-wiu6'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(username))
        wta.assertHasAttribute('user', username, 'user_groups', 'None')

    def test_web_user_add_superuser(self):
        # Adds a super user
        username = self.gvar['user'] + '-wiu7'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(username))
        self.assertTrue(self.page.superuser_box_checked())
        wta.assertHasAttribute('user', username, 'is_superuser', '1')

    def test_web_user_add_regular_user(self):
        # Adds a non-super user
        username = self.gvar['user'] + '-wiu8'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(username))
        self.assertFalse(self.page.superuser_box_checked())
        wta.assertHasAttribute('user', username, 'is_superuser', '0')

    def test_web_user_add_without_username(self):
        # Tries to add a user without a username
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_user_add_with_conflicting_username(self):
        # Tries to add a user with a username that's already taken
        username = self.gvar['user'] + '-wiu1'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasAttribute('user', username, 'is_superuser', '0')

    def test_web_user_add_name_with_symbols(self):
        # Tries to add a user with symbols in their name
        username = 'inv@|id-web-te$t'
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_name_with_two_dashes(self):
        # Tries to add a user with two dashes in their name
        username = 'invalid--web--test'
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_name_with_uppercase(self):
        # Tries to add a user with uppercase letters in their name
        username = 'INVALID-WEB-TEST'
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_name_with_starting_ending_dash(self):
        # Tries to add a user with starting and ending dashes in their name
        username = '-invalid-web-test-'
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_name_too_long(self):
        # Tries to add a user with a name that is too long for the database
        username = self.oversize['varchar_32']
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)
     
    def test_web_user_add_without_password(self):
        # Tries to add a user without a password
        username = self.gvar['user'] + '-wiu9'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('user', username)

    def test_web_user_add_password_mismatched(self):
        # Tries to add a user with a non-matching "confirm password"
        username = self.gvar['user'] + '-wiu9'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(self.gvar['user_secret'], 'incorrect_password')
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('user', username)

    def test_web_user_add_password_too_short(self):
        # Tries to add a user with a password that's too short
        username = self.gvar['user'] + '-wiu9'
        group_name = self.gvar['user'] + '-wig3'
        password = 'Aa1'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(password)
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_password_without_uppercase(self):
        # Tries to add a user with a password without uppercase letters
        username = self.gvar['user'] + '-wiu9'
        group_name = self.gvar['user'] + '-wig3'
        password = 'abcd1234'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(password)
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_password_without_lowercase(self):
        # Tries to add a user with a password without lowercase letters
        username = self.gvar['user'] + '-wiu9'
        group_name = self.gvar['user'] + '-wig3'
        password = 'ABCD1234'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(password)
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_add_password_without_numbers(self):
        # Tries to add a user with a password without numbers
        username = self.gvar['user'] + '-wiu9'
        group_name = self.gvar['user'] + '-wig3'
        password = 'ABCDabcd'
        self.page.click_add_button()
        self.page.type_username(username)
        self.page.type_password(password)
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_update_password(self):
        # Changes a user's password
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.type_password(username + '-password')
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_user_update_password_mismatched(self):
        # Tries to change a user's password with a non-matching "confirm password"
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.type_password(username + '-password', 'incorrect_password')
        self.page.click_update_user()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_user_update_password_too_short(self):
        # Tries to change a user's password to one that's too short
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.type_password('Aa1')
        self.page.click_update_user()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_user_update_password_without_uppercase(self):
        # Tries to change a user's password to one without uppercase letters
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.type_password('abcd1234')
        self.page.click_update_user()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_user_update_password_without_lowercase(self):
        # Tries to change a user's password to one without lowercase letters
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.type_password('ABCD1234')
        self.page.click_update_user()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_user_update_password_without_numbers(self):
        # Tries to change a user's password to one without numbers
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.type_password('ABCDabcd')
        self.page.click_update_user()
        self.assertTrue(self.page.error_message_displayed())

    @unittest.skip("No current infrastructure to test this.")
    def test_web_user_update_cert_cn(self):
        # Changes a user's certificate common name
        pass

    @unittest.skip("No current infrastructure to test this.")
    def test_web_user_update_cert_cn_too_long(self):
        # Tries to change a user's certificate common name to one that's too long for the database
        pass

    def test_web_user_update_superuser(self):
        # Changes a regular user to a super user
        username = self.gvar['user'] + '-wiu4'
        self.page.click_side_button(username)
        self.page.click_superuser_checkbox()
        self.page.click_update_user()
        self.assertTrue(self.page.superuser_box_checked())
        wta.assertHasAttribute('user', username, 'is_superuser', '1')

    def test_web_user_update_group_add(self):
        # Adds a user to a group
        username = self.gvar['user'] + '-wiu4'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_side_button(username)
        self.page.click_group_checkbox(group_name)
        self.page.click_update_user()
        self.assertTrue(self.page.group_box_checked(group_name))
        wta.assertHasAttribute('user', username, 'user_groups', group_name)

    def test_web_user_update_group_remove(self):
        # Removes a user from a group
        username = self.gvar['user'] + '-wiu4'
        group_name = self.gvar['user'] + '-wig1'
        self.page.click_side_button(username)
        self.page.click_group_checkbox(group_name)
        self.page.click_update_user()
        self.assertFalse(self.page.group_box_checked(group_name))
        wta.assertHasNotAttribute('user', username, 'user_groups', group_name)

    def test_web_user_delete(self):
        # Deletes a user
        username = self.gvar['user'] + '-wiu3'
        self.page.click_side_button(username)
        self.page.click_delete_button()
        self.page.click_delete_modal()
        self.assertFalse(self.page.side_button_exists(username))
        wta.assertNotExists('user', username)

    def test_web_user_delete_cancel(self):
        # Tries to delete a user but clicks cancel
        username = self.gvar['user'] + '-wiu1'
        self.page.click_side_button(username)
        self.page.click_delete_button()
        self.page.click_delete_cancel()
        self.assertTrue(self.page.side_button_exists(username))
        wta.assertExists('user', username)

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebUserSuperUserFirefox(TestWebUserCommon):
    """A class to test user operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['users'], browser='firefox')
            super(TestWebUserSuperUserFirefox, cls).setUpClass()
            print("\nUser Tests:")
        except:
            print("Error in test setup")
            super(TestWebUserSuperUserFirefox, cls).tearDownClass()
            raise

class TestWebUserSuperUserChromium(TestWebUserCommon):
    """A class to test user operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['users'], browser='chromium')
            super(TestWebUserSuperUserChromium, cls).setUpClass()
            print("\nUser Tests (Chromium):")
        except:
            print("Error in test setup")
            super(TestWebUserSuperUserChromium, cls).tearDownClass()
            raise

class TestWebUserSuperUserOpera(TestWebUserCommon):
    """A class to test user operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['users'], browser='opera')
            super(TestWebUserSuperUserOpera, cls).setUpClass()
            print("\nUser Tests (Opera):")
        except:
            print("Error in test setup")
            super(TestWebUserSuperUserOpera, cls).tearDownClass()
            raise

class TestWebUserSuperUserChrome(TestWebUserCommon):
    """A class to test user operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['users'], browser='chrome')
            super(TestWebUserSuperUserChrome, cls).setUpClass()
            print("\nUser Tests (Chrome):")
        except:
            print("Error in test setup")
            super(TestWebUserSuperUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebUserSuperUserFirefox,
              TestWebUserSuperUserChromium,
              TestWebUserSuperUserOpera,
              TestWebUserSuperUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, False)
    runner.run(suite)
