from django.test import TestCase

from ..models import User


class UserModelTest(TestCase):
    """Test user model

    Arguments:
        TestCase {TestCase} -- django TestCase class
    """
    def test_user_creation_without_email(self):
        with self.assertRaisesMessage(ValueError, 'Users must have an email address'):
            User.objects.create_user(
                email=None,
                first_name='John',
                last_name='Sanders',
                password='awesome',
            )

    def test_user_creation_without_password(self):
        with self.assertRaisesMessage(ValueError, 'Users must have a password'):
            User.objects.create_user(
                email='user@example.com',
                first_name='John',
                last_name='Sanders',
            )

    def test_user_creation_without_first_name(self):
        with self.assertRaisesMessage(ValueError, 'Users must have a first name'):
            User.objects.create_user(
                email='user@example.com',
                first_name='',
                last_name='Sanders',
                password='awesome',
            )

    def test_user_creation_without_last_name(self):
        with self.assertRaisesMessage(ValueError, 'Users must have a last name'):
            User.objects.create_user(
                email='user@example.com',
                first_name='John',
                last_name='',
                password='awesome',
            )

    def test_user_creation(self):
        user = User.objects.create_user(
            email='user@example.com',
            first_name='John',
            last_name='Sanders',
            password='awesome',
        )

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'user@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Sanders')
        self.assertTrue(user.check_password('awesome'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.get_full_name(), 'John Sanders')
        self.assertEqual(user.get_short_name(), 'John')
        self.assertTrue(user.has_perm('users.view_user'))
        self.assertTrue(user.has_module_perms('users'))
        self.assertEqual(str(user), 'John Sanders')

    def test_super_user_creation(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Justin',
            last_name='Heavyman',
            password='awesome_secret'
        )

        self.assertIsInstance(admin_user, User)
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.first_name, 'Justin')
        self.assertEqual(admin_user.last_name, 'Heavyman')
        self.assertTrue(admin_user.check_password('awesome_secret'))
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_superuser)
