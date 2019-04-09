# from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from ..models import User
from ..serializers import UserSerializer


class BaseViewTest(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user_data = {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Sanders',
            'password': 'awesome',
            'phone_number': '23487456730',
            'address': 'don\'t come to my place',
        }
        User.objects.create_user(**self.user_data)


class RegisterViewTest(BaseViewTest):
    def test_register_user_with_incomplete_data(self):
        incomplete_user_data = {
            'first_name': 'Jonathan',
            'last_name': 'Johnson',
            'password': 'awesome',
        }
        response = self.client.post(reverse('create_account'), incomplete_user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertCountEqual(set(data['error']), set(['email', 'phone_number', 'address']))

    def test_register_user_with_invalid_email(self):
        invalid_user_data = {
            'email': 'jonathanexample.com',
            'first_name': 'Jonathan',
            'last_name': 'Johnson',
            'password': 'awesome',
            'phone_number': '23487456730',
            'address': 'don\'t come to my place',
        }
        response = self.client.post(reverse('create_account'), invalid_user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertCountEqual(set(data['error']), set(['email']))

    def test_register_user_with_invalid_first_and_last_name(self):
        invalid_user_data = {
            'email': 'jonathan@example.com',
            'first_name': 'Jona8#$',
            'last_name': '+Johnson!',
            'password': 'awesome',
            'phone_number': '23487456730',
            'address': 'don\'t come to my place',
        }
        response = self.client.post(reverse('create_account'), invalid_user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertCountEqual(set(data['error']), set(['first_name', 'last_name']))

    def test_register_user_with_complete_data(self):
        valid_and_complete_user_data = {
            'email': 'jonathan@example.com',
            'first_name': 'Jonathan',
            'last_name': 'Johnson',
            'password': 'awesome',
            'phone_number': '23487456730',
            'address': 'don\'t come to my place',
        }
        response = self.client.post(reverse('create_account'), valid_and_complete_user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'User registered')
        self.assertEqual(set(data['data']), set(['token']))
        self.assertIsInstance(data['data']['token'], str)

    def test_register_user_with_existing_email_address(self):
        response = self.client.post(reverse('create_account'), self.user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertEqual(set(data['error']), set(['email']))


class LoginViewTest(BaseViewTest):
    def test_login_with_incomplete_credentials(self):
        without_password = {
            'email': 'user@example.com'
        }
        without_email = {
            'password': 'awesome'
        }
        response = self.client.post(reverse('login'), without_password, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Please provide both email and password')

        response = self.client.post(reverse('login'), without_email, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Please provide both email and password')

    def test_login_with_wrong_credentials(self):
        wrong_credentials = {
            'email': 'notexisting@example.com',
            'password': 'wrong'
        }
        response = self.client.post(reverse('login'), wrong_credentials, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Username or password incorrect')

    def test_login_with_valid_credentials(self):
        valid_credentials = {
            'email': 'user@example.com',
            'password': 'awesome'
        }
        response = self.client.post(reverse('login'), valid_credentials, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'Use logged in')
        self.assertEqual(set(data['data']), set(['token']))
        self.assertIsInstance(data['data']['token'], str)
