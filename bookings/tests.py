import pytz
from datetime import datetime
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from users.models import User
from flights.models import Flight
from .models import Booking


class BaseViewTest(APITestCase):
    """Base view test class

    Arguments:
        APITestCase {APITestCase} -- rest_framework APITestCase class
    """
    MOCK_NOW = datetime(2019, 4, 10, 9, 00, tzinfo=pytz.timezone('utc'))
    client = APIClient()
    token = []

    def setUp(self):
        self.user_data = [{
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'West',
            'password': 'awesome',
            'phone_number': 2348023894574,
        },{
            'email': 'user_2@example.com',
            'first_name': 'Sam',
            'last_name': 'Edgar',
            'password': 'awesome',
            'phone_number': 2348023894576,
        }]
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
        self.user_1 = self.create_user(self.user_data[0])
        self.user_2 = self.create_user(self.user_data[1])

        self.login_user({
            'email': 'admin@example.com',
            'password': 'awesomeadmin'
        })
        self.login_user({
            'email': 'user@example.com',
            'password': 'awesome'
        })
        self.login_user({
            'email': 'user_2@example.com',
            'password': 'awesome'
        })

        self.flight_1 = self.create_flight(self.flight_data[0])
        self.flight_2 = self.create_flight(self.flight_data[1])

    def create_user(self, data, admin=False):
        if admin:
            return User.objects.create_superuser(**data)
        else:
            return User.objects.create_user(**data)

    def login_user(self, data):
        response = self.client.post(reverse('login'), data, format='json')
        self.token.append(response.data['data']['token'])

    def create_flight(self, data):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            data.update({'created_by': self.admin})
            return Flight.objects.create(**data)


class BaseDetailViewTest(BaseViewTest):
    """Base detail view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """
    def setUp(self):
        super().setUp()

        self.booking_1 = self.book_flight({
            'flight_id': self.flight_1,
            'ticket_number': 'EF343F'
        }, self.user_1)
        self.booking_2 = self.book_flight({
            'flight_id': self.flight_2,
            'ticket_number': 'ST54F3'
        }, self.user_2)

    def book_flight(self, data, user):
        data.update({
            'passenger_id': user
        })
        return Booking.objects.create(**data)


class BookingListViewTest(BaseViewTest):
    """Booking list view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """
    def test_booking_flight_without_token(self):
        response = self.client.post(reverse('booking_list'), {}, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_booking_non_existing_flight(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.post(reverse('booking_list'), {'flight_id': 999999}, format='json')
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Could not book the flight')
        self.assertEqual(data['error']['flight_id'],
                         ['Flight with the id "999999" does not exist'])

    def test_booking_flight_successfully(self):
        with patch('bookings.views.email_ticket.delay') as mock_delay:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
            response = self.client.post(reverse('booking_list'),
                                        {'flight_id': self.flight_1.id},
                                        format='json')
            data = response.data

            self.assertEqual(response.status_code, 201)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Ticket booked')
            self.assertEqual(data['data']['flight_status'], 'Booked')
            self.assertIsInstance(data['data']['ticket_number'], str)
            self.assertEqual(data['data']['passenger']['id'], self.user_1.id)
            self.assertEqual(data['data']['flight']['id'], self.flight_1.id)
            self.assertEqual(data['data']['amount_paid'], '0.00')
            self.assertIsNone(data['data']['reserved_at'])
            self.assertTrue(mock_delay.called)

            response = self.client.post(reverse('booking_list'),
                                        {'flight_id': self.flight_1.id},
                                        format='json')
            data = response.data

            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Could not book the flight')
            self.assertEqual(data['error']['non_field_errors'], ['Ticket already booked'])

    def test_get_ticket_status_without_token(self):
        response = self.client.get(reverse('booking_list'), {'ticket_number': 'ticket'})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_get_ticket_status_with_invalid_ticket(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('booking_list'), {'ticket': 'FR56@D$'})
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Invalid ticket number')
        self.assertEqual(set(data['error']), set(['ticket']))
        self.assertEqual(data['error']['ticket'],
                         ['Ticket number invalid please provide a valid ticket'])

    def test_get_ticket_status_with_non_existing_ticket(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('booking_list'), {'ticket': 'none01'})
        data = response.data

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Ticket not found')

    def test_get_ticket_status_with_valid_ticket(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        with patch('bookings.views.email_ticket.delay') as mock_delay:
            booking = self.client.post(reverse('booking_list'),
                                        {'flight_id': self.flight_1.id},
                                        format='json')

        response = self.client.get(reverse('booking_list'),
                                   {'ticket': booking.data['data']['ticket_number']})
        data = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(data['message'], 'Booking retrieved')
        self.assertEqual(data['data']['ticket_number'], booking.data['data']['ticket_number'])

    def test_get_flight_reservations_without_query_params(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('booking_list'))
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Query params required')

    def test_get_flight_reservations_with_wrong_query_params(self):
        query_params = {
            'ticket': 'FT533F',
            'wrong_key': 'this'
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('booking_list'), query_params)
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Invalid query params - wrong_key')

    def test_get_flight_reservations_with_invalid_query_params(self):
        query_params = {
            'flight': self.flight_1.id,
            'date': 'Wrong_date',
            'status': 'Wrong_status'
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('booking_list'), query_params)
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Provide valid query parameters')
        self.assertEqual(set(data['error']), set(['date', 'status']))

    def test_get_flight_reservations_with_wrong_query_params_combination(self):
        query_params = {
            'ticket': 'FR56@D$',
            'date': 'Wrong_date',
            'status': 'Reserved'
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.get(reverse('booking_list'), query_params)
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'],
                         'Unsupported query params combination: provide flight, date and status')

    def test_get_flight_reservations_successfully_for_a_specific_day(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            # Book a flight
            with patch('bookings.views.email_ticket.delay') as mock_delay:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
                booking = self.client.post(reverse('booking_list'),
                                            {'flight_id': self.flight_1.id},
                                            format='json')

            # Reserve the booked flight
            with patch('bookings.views.email_reservation.delay') as mock_delay:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
                self.client.put(
                    reverse('booking_detail', kwargs={'booking_pk': booking.data['data']['id']}),
                    {'amount_paid': 300},
                    format='json'
                )

            query_params = {
                'flight': self.flight_1.id,
                'date': '2019-04-12',
                'status': 'Reserved'
            }
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
            response = self.client.get(reverse('booking_list'), query_params)
            data = response.data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Flight retrieved')
            self.assertEqual(data['data']['count'], 1)

    def test_get_flight_bookings_successfully_for_a_specific_day(self):
        with patch('django.utils.timezone.now', return_value=self.MOCK_NOW):
            # Book a flight
            with patch('bookings.views.email_ticket.delay') as mock_delay:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
                booking = self.client.post(reverse('booking_list'),
                                            {'flight_id': self.flight_1.id},
                                            format='json')

            query_params = {
                'flight': self.flight_1.id,
                'date': '2019-04-12',
                'status': 'Booked'
            }
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
            response = self.client.get(reverse('booking_list'), query_params)
            data = response.data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Flight retrieved')
            self.assertEqual(data['data']['count'], 1)


class BookingDetailViewTest(BaseDetailViewTest):
    """Booking detail view test class

    Arguments:
        BaseViewTest {APITestCase} -- BaseViewTest class
    """
    def test_reserve_flight_without_token(self):
        response = self.client.put(
            reverse('booking_detail', kwargs={'booking_pk': self.booking_1.id}),
            {'flight_id': self.flight_1.id},
            format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_reserve_non_existing_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.put(
            reverse('booking_detail', kwargs={'booking_pk': 99999}),
            {'flight_id': self.flight_1.id},
            format='json')
        data = response.data

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Booking not found')

    def test_reserve_non_user_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[2]}')
        response = self.client.put(
            reverse('booking_detail', kwargs={'booking_pk': self.booking_1.id}),
            {'flight_id': self.flight_1.id},
            format='json')
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'You have not booked this flight')

    def test_reserve_user_booking_without_amount_paid(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.put(
            reverse('booking_detail', kwargs={'booking_pk': self.booking_1.id}),
            {},
            format='json')
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Flight not reserved')
        self.assertEqual(data['error']['non_field_errors'], ['Field amount paid is required'])

    def test_reserve_user_booking_with_incorrect_amount(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
        response = self.client.put(
            reverse('booking_detail', kwargs={'booking_pk': self.booking_1.id}),
            {'amount_paid': 200},
            format='json')
        data = response.data

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Error')
        self.assertEqual(data['message'], 'Flight not reserved')
        self.assertEqual(data['error']['non_field_errors'], ['Amount paid is not equal to the flight cost'])

    def test_reserve_user_booking_successfully(self):
        with patch('bookings.views.email_reservation.delay') as mock_delay:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token[1]}')
            response = self.client.put(
                reverse('booking_detail', kwargs={'booking_pk': self.booking_1.id}),
                {'amount_paid': 300},
                format='json')
            data = response.data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['status'], 'Success')
            self.assertEqual(data['message'], 'Flight reserved')
            self.assertEqual(data['data']['flight_status'], 'Reserved')
            self.assertEqual(data['data']['amount_paid'], '300.00')
            self.assertIsNotNone(data['data']['reserved_at'])
            self.assertTrue(mock_delay.called)

            response = self.client.put(
                reverse('booking_detail', kwargs={'booking_pk': self.booking_1.id}),
                {'amount_paid': 300},
                format='json')
            data = response.data

            self.assertEqual(response.status_code, 409)
            self.assertEqual(data['status'], 'Error')
            self.assertEqual(data['message'], 'Flight already reserved')
