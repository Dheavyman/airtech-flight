from django.test import TestCase
from django.utils.encoding import force_text

from ..models import User
from ..forms import UserCreationForm, UserChangeForm


class UserCreationFormTest(TestCase):
    """User creation form test class

    Arguments:
        TestCase {TestCase} -- django TestCase class
    """
    def test_create_user_form_with_noncomfirmed_password(self):
        data = {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Sanders',
            'password1': 'awesome',
            'password2': 'not_awesome',
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_user_creation_form_with_valid_data(self):
        data = {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Sanders',
            'password1': 'awesome',
            'password2': 'awesome',
        }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'user@example.com')

    def test_user_creation_form_with_existing_user_email(self):
        user = User.objects.create(
            email='user@example.com',
            first_name= 'John',
            last_name= 'Sanders',
            password= 'awesome',
        )
        data = {
            'email': user.email,
            'first_name': 'Jackie',
            'last_name': 'Chang',
            'password1': 'another_awesome',
            'password2': 'another_awesome',
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors, ['User with this Email address already exists.'])


class UserChangeFormTest(TestCase):
    """User change form test class

    Arguments:
        TestCase {TestCase} -- django TestCase class
    """
    def test_change_user_form_with_valid_data(self):
        user = User.objects.create(
            email='user@example.com',
            first_name= 'John',
            last_name= 'Sanders',
            password= 'awesome',
        )
        data = {
            'email': user.email,
            'first_name': 'Johnson',
            'last_name': user.last_name,
            'password': user.password
        }
        form = UserChangeForm(data=data, instance=user)
        self.assertTrue(form.is_valid())
