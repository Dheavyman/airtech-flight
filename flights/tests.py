import pytz
from datetime import datetime
from unittest.mock import patch

from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from users.models import User
from .models import Flight


class BaseViewTest(APITestCase):
    """Base view test class

    Arguments:
        APITestCase {APITestCase} -- rest_framework APITestCase class
    """
    MOCK_NOW = datetime(2019, 4, 10, 9, 00, tzinfo=pytz.timezone('utc'))
    client = APIClient()
    token = []

    def setUp(self):
        self.user_data = {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'West',
            'password': 'awesome',
            'phone_number': 2348023894574,
        }
        self.admin_data = {
            'email': 'admin@example.com',
            'first_name': 'Micheal',
            'last_name': 'Perez',
            'password': 'awesomeadmin',
        }
        self.flight_data = [{
            'flight_number': 'FE3433',
            'departure_datetime': '2019-04-12T09:05Z',
            'arrival_datetime': '2019-04-13T12:00Z',
            'flight_cost': 300,
            'departing': 'Lagos',
            'departing_airport': 'LOS',
            'destination': 'Dubai',
            'destination_airport': 'DXB',
        },{
            'flight_number': 'TNE245',
            'departure_datetime': '2019-04-20T00:05Z',
            'arrival_datetime': '2019-04-20T13:20Z',
            'flight_cost': 250,
            'departing': 'England',
            'departing_airport': 'ENG',
            'destination': 'China',
            'destination_airport': 'CHI',
        }]

        self.admin = self.create_user(self.admin_data, admin=True)
        self.create_user(self.user_data)

        self.login_user({
            'email': 'admin@example.com',
            'password': 'awesomeadmin'
        })
        self.login_user({
            'email': 'user@example.com',
            'password': 'awesome'
        })

    def create_user(self, data, admin=False):
        if admin:
            return User.objects.create_superuser(**data)
        else:
            return User.objects.create_user(**data)

    def login_user(self, data):
        response = self.client.post(reverse('login'), data, format='json')
        self.token.append(response.data['data']['token'])


class BaseDetailViewTest(BaseViewTest):
    """Base detail view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """
    def setUp(self):
        super().setUp()

        self.flight_1 = self.create_flight(self.flight_data[0])
        self.flight_2 = self.create_flight(self.flight_data[1])

    def create_flight(self, data):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            data.update({'created_by': self.admin})
            return Flight.objects.create(**data)


class FlightListViewTest(BaseViewTest):
    """Flight list view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """
    def test_create_flight_without_token(self):
        response = self.client.post(reverse('flight_list'), {}, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_create_flight_with_non_admin_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.post(reverse('flight_list'), {}, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Request forbidden, must be an admin')

    def test_create_flight_with_admin_token(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.post(reverse('flight_list'), self.flight_data[0], format='json')
            data = response.data

            self.assertEqual(response.status_code, 201)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'flight created')
            self.assertEqual(data['data']['flight_number'], self.flight_data[0]['flight_number'])

    def test_create_flight_with_incomplete_data(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.post(reverse('flight_list'), {}, format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not create the flight')
            self.assertEqual(set(data['error']),
                             set(['flight_number', 'destination_airport', 'departing_airport',
                                  'departing', 'departure_datetime', 'arrival_datetime',
                                  'destination']))

    def test_create_flight_with_invalid_flight_number(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            self.flight_data[0].update({'flight_number': 'DFE$453%'})
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.post(reverse('flight_list'), self.flight_data[0], format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not create the flight')
            self.assertEqual(set(data['error']), set(['flight_number']))
            self.assertEqual(data['error']['flight_number'],
                             ['Must be only alphanumeric characters'])

    def test_create_flight_with_invalid_date(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            self.flight_data[0].update({'departure_datetime': '2019-04-05T09:05Z'})
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.post(reverse('flight_list'), self.flight_data[0], format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not create the flight')
            self.assertEqual(set(data['error']), set(['departure_datetime']))
            self.assertEqual(data['error']['departure_datetime'],
                             ['Departure_datetime must be at least 24 hours ahead'])

            self.flight_data[0].update({
                'departure_datetime': '2019-04-12T09:05Z',
                'arrival_datetime': '2019-04-11T12:00Z',
            })
            response = self.client.post(reverse('flight_list'), self.flight_data[0], format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not create the flight')
            self.assertEqual(data['error']['non_field_errors'],
                             ['Arrival_datetime must occur after departure_datetime'])

    def test_get_flights(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('flight_list'), format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'Flights retrieved')
        self.assertIsInstance(data['data'], list)

    def test_get_flights_without_token(self):
        response = self.client.get(reverse('flight_list'), format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')


class FlightDetailViewTest(BaseDetailViewTest):
    """Flight detail view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """
    def test_get_fight_without_token(self):
        response = self.client.get(reverse('flight_detail',
                                   kwargs={'flight_pk': self.flight_1.id}),
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_get_fight_with_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('flight_detail',
                                   kwargs={'flight_pk': self.flight_1.id}),
                                   format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'Flight retrieved')
        self.assertEqual(data['data']['id'], self.flight_1.id)

    def test_get_non_existing_flight(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('flight_detail',
                                   kwargs={'flight_pk': 9999}),
                                   format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Flight not found')

    def test_edit_flight_without_token(self):
        response = self.client.put(reverse('flight_detail',
                                   kwargs={'flight_pk': self.flight_1.id}),
                                   {},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_edit_flight_with_non_admin_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.put(reverse('flight_detail',
                                   kwargs={'flight_pk': self.flight_1.id}),
                                   {},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Request forbidden, must be an admin')

    def test_edit_flight_with_admin_token(self):
        self.flight_data[0].update({
            'flight_cost': 280,
            'created_by': self.admin.id
        })
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.put(reverse('flight_detail', kwargs={'flight_pk': self.flight_1.id}),
                                    self.flight_data[0],
                                    format='json')
            data = response.data

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Flight updated')
            self.assertEqual(data['data']['flight_cost'], '280.00')

    def test_edit_non_existing_flight(self):
        self.flight_data[0].update({
            'flight_cost': 280,
            'created_by': self.admin.id
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
        response = self.client.put(reverse('flight_detail', kwargs={'flight_pk': 10000}),
                                   self.flight_data[0],
                                   format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Flight not found')

    def test_edit_flight_with_invalid_date(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            self.flight_data[0].update({
                'created_by': self.admin.id
            })
            self.flight_data[0].update({'departure_datetime': '2019-04-05T09:05Z'})
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
            response = self.client.put(
                reverse('flight_detail', kwargs={'flight_pk': self.flight_1.id}),
                self.flight_data[0], format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not update flight')
            self.assertEqual(set(data['error']), set(['departure_datetime']))
            self.assertEqual(data['error']['departure_datetime'],
                             ['Departure_datetime must be at least 24 hours ahead'])

            self.flight_data[0].update({
                'departure_datetime': '2019-04-12T09:05Z',
                'arrival_datetime': '2019-04-11T12:00Z',
            })
            response = self.client.put(
                reverse('flight_detail', kwargs={'flight_pk': self.flight_1.id}),
                self.flight_data[0],
                format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not update flight')
            self.assertEqual(data['error']['non_field_errors'],
                             ['Arrival_datetime must occur after departure_datetime'])

    def test_delete_flight_without_token(self):
        response = self.client.delete(reverse('flight_detail',
                                   kwargs={'flight_pk': self.flight_1.id}),
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_delete_flight_with_non_admin_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.delete(reverse('flight_detail',
                                   kwargs={'flight_pk': self.flight_1.id}),
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Request forbidden, must be an admin')

    def test_delete_flight_with_admin_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[0]}')
        response = self.client.delete(
            reverse('flight_detail', kwargs={'flight_pk': self.flight_1.id}),
            format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'Flight deleted')

        response = self.client.delete(
            reverse('flight_detail', kwargs={'flight_pk': self.flight_1.id}),
            format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Flight not found')
