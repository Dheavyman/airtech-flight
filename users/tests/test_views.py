import tempfile
from PIL import Image
from unittest import mock
from shutil import rmtree

from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.test import override_settings

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from ..models import User
from ..serializers import UserSerializer

def get_temporary_image(temp_file):
    size = (350, 350)
    color = (0, 0, 0, 0)
    image = Image.new('RGB', size, color)
    image.save(temp_file)

    return temp_file


class BaseViewTest(APITestCase):
    """Base view test class

    Arguments:
        APITestCase {APITestCase} -- rest_framework APITestCase class
    """

    client = APIClient()

    def setUp(self):
        self.user_data = [{
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Sanders',
            'password': 'awesome',
            'phone_number': '23487456730',
            'address': 'don\'t come to my place',
        },{
            'email': 'another_user@example.com',
            'first_name': 'James',
            'last_name': 'West',
            'password': 'another_awesome',
            'address': 'don\'t come to my place',
        }]
        self.valid_credentials = [{
            'email': 'user@example.com',
            'password': 'awesome'
        },{
            'email': 'another_user@example.com',
            'password': 'another_awesome'
        }]

        self.create_user(self.user_data[0])
        self.create_user(self.user_data[1])

    def create_user(self, data):
        User.objects.create_user(**data)


class ProfilePhotoBaseViewTest(BaseViewTest):
    """Profile photo base view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """

    token = []

    def setUp(self):
        super().setUp()
        self.media_folder = tempfile.mkdtemp()

        self.login_user(self.valid_credentials[0])
        self.login_user(self.valid_credentials[1])

    def tearDown(self):
        rmtree(self.media_folder)

    def login_user(self, data):
        response = self.client.post(reverse('login'), data, format='json')
        self.token.append(response.data['data']['token'])


class RegisterViewTest(BaseViewTest):
    """Register view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """

    def test_register_user_with_incomplete_data(self):
        incomplete_user_data = {}
        response = self.client.post(reverse('create_account'), incomplete_user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertCountEqual(set(data['error']),
                              set(['email', 'first_name', 'last_name', 'phone_number', 'password',
                                   'address']))

    def test_register_user_with_invalid_email(self):
        invalid_user_data = {
            'email': 'jonathanexample.com',
            'first_name': 'Jonathan',
            'last_name': 'Johnson',
            'password': 'awesome',
            'phone_number': '23480456730',
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
            'phone_number': '23480456730',
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
            'phone_number': '23480456730',
            'address': 'don\'t come to my place',
        }
        response = self.client.post(reverse('create_account'),
                                    valid_and_complete_user_data, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'User registered')
        self.assertEqual(set(data['data']), set(['token']))
        self.assertIsInstance(data['data']['token'], str)

    def test_register_user_with_existing_email_address(self):
        self.user_data[0].update({'phone_number': 237034823481})
        response = self.client.post(reverse('create_account'), self.user_data[0], format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertEqual(set(data['error']), set(['email']))

    def test_register_user_with_existing_phonenumber(self):
        self.user_data[0].update({'email': 'test@example.com'})
        response = self.client.post(reverse('create_account'), self.user_data[0], format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not register user')
        self.assertEqual(set(data['error']), set(['phone_number']))


class LoginViewTest(BaseViewTest):
    """Login view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """

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
        response = self.client.post(reverse('login'), self.valid_credentials[0], format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'Use logged in')
        self.assertEqual(set(data['data']), set(['token']))
        self.assertIsInstance(data['data']['token'], str)


class ProfilePhotoViewTest(ProfilePhotoBaseViewTest):
    """Profile photo view test class

    Arguments:
        ProfilePhotoBaseViewTest {APITestCase} -- ProfilePhotoBaseViewTest class
    """

    def test_passport_photo_upload_without_token(self):
        user = User.objects.get(email='user@example.com')
        response = self.client.put(reverse('profile_photo', kwargs={'pk': user.id}),
                                   {'passport_photo': 'test_photo_file'},
                                   format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_passport_photo_upload_without_photo(self):
        user = User.objects.get(email='user@example.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
        response = self.client.put(reverse('profile_photo', kwargs={'pk': user.id}),
                                   {},
                                   format='multipart')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not update passport photo')
        self.assertEqual(set(data['error']), set(['passport_photo']))

    def test_passport_photo_upload_for_another_user(self):
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        test_photo = get_temporary_image(temp_file)
        test_photo.seek(0)
        another_user = User.objects.get(email='another_user@example.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
        response = self.client.put(reverse('profile_photo', kwargs={'pk': another_user.id}),
                                   {'passport_photo': test_photo},
                                   format='multipart')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Request forbidden, not users profile')

    @mock.patch('storages.backends.s3boto3.S3Boto3Storage', FileSystemStorage)
    def test_passport_photo_upload(self):
        with override_settings(MEDIA_ROOT=self.media_folder):
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
            test_photo = get_temporary_image(temp_file)
            test_photo.seek(0)
            user = User.objects.get(email='user@example.com')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.put(reverse('profile_photo', kwargs={'pk': user.id}),
                                       {'passport_photo': test_photo},
                                       format='multipart')
            data = response.data

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Passport photo updated')
            self.assertEqual(data['data']['id'], user.id)
            self.assertIn('profile_pics/', data['data']['passport_photo'])

    def test_passport_photo_delete_without_token(self):
        user = User.objects.get(email='user@example.com')
        response = self.client.delete(reverse('profile_photo', kwargs={'pk': user.id}),
                                      format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_passport_photo_delete_for_another_user(self):
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        test_photo = get_temporary_image(temp_file)
        test_photo.seek(0)
        another_user = User.objects.get(email='another_user@example.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
        response = self.client.delete(reverse('profile_photo', kwargs={'pk': another_user.id}),
                                      {'passport_photo': test_photo},
                                      format='multipart')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Request forbidden, not users profile')

    @mock.patch('storages.backends.s3boto3.S3Boto3Storage', FileSystemStorage)
    def test_passport_photo_delete(self):
        with override_settings(MEDIA_ROOT=self.media_folder):
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
            test_photo = get_temporary_image(temp_file)
            test_photo.seek(0)
            user = User.objects.get(email='user@example.com')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            self.client.put(reverse('profile_photo', kwargs={'pk': user.id}),
                            {'passport_photo': test_photo},
                            format='multipart')
            response = self.client.delete(reverse('profile_photo', kwargs={'pk': user.id}),
                                          format='multipart')
            data = response.data

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Passport photo deleted')

    def test_passport_photo_delete_without_photo(self):
        user = User.objects.get(email='another_user@example.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.delete(reverse('profile_photo', kwargs={'pk': user.id}),
                                      format='multipart')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'User does not have a passport_photo')
