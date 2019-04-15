import json

from locust import HttpLocust, TaskSet, task

class UserBookFlight(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post('/api/v1/auth/login', {
            'email': 'jonathan@example.com',
            'password': 'awesome'
        })
        json_data = json.loads(response._content)
        self.token = json_data['data']['token']

    @task(5)
    def get_flight_status(self):
        self.client.get('/api/v1/bookings?ticket=82BDD8', headers={
            'Authorization': f'Bearer {self.token}'
        })

    @task(3)
    def get_flights(self):
        self.client.get('/api/v1/flights', headers={
            'Authorization': f'Bearer {self.token}'
        })

    @task(1)
    def get_flight_reservations(self):
        self.client.get('/api/v1/bookings?flight=4&date=2019-04-14&status=reserved', headers={
            'Authorization': f'Bearer {self.token}'
        })

    @task(2)
    def get_flight_bookings(self):
        self.client.get('/api/v1/bookings?flight=4&date=2019-04-14&status=booked', headers={
            'Authorization': f'Bearer {self.token}'
        })

    # TODO: Test put methods which are idempotent


class ApplicationUser(HttpLocust):
    task_set = UserBookFlight
    min_wait = 5000
    max_wait = 8000
