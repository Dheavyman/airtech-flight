[![Build Status](https://travis-ci.com/Dheavyman/airtech-flight.svg?branch=develop)](https://travis-ci.com/Dheavyman/airtech-flight)
[![Coverage Status](https://coveralls.io/repos/github/Dheavyman/airtech-flight/badge.svg?branch=develop)](https://coveralls.io/github/Dheavyman/airtech-flight?branch=develop)

# Airtech-flight
Airtech-flight is an application for managing flight booking system.

## Table of Contents
- [Application Features](#application-features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Running the tests](#running-the-tests)
- [Built With](#built-with)
- [License](#license)
- [Credits](#credits)

## Application features
* Users can create an account
* Users can upload, change and delete their passport photograph using AWS as a remote server.
* Admin can create, update and delete a flight
* Users can get flight details
* Users can book tickets and receive their ticket via email
* Users can check the status of their flight
* Users can make flight reservations and receive email notification
* Users can purchase tickets
* Users are reminded of their flight schedule automatically via email, a day before their travel date
* Users can get the number of people that made reservation for a particular flight on a specific day

## Prerequisites
* Install python(version 3.6 and above) and Postgresql database locally
* Create an AWS account and an S3 bucket
* Create a gmail account

## Getting started
Follow the steps below to get the application running locally:
```
# Create development database using postgres createdb command
>$ createdb airtech-flight

# Clone the repository
>$ git clone https://github.com/Dheavyman/airtech-flight.git

# Change directory into the project
>$ cd airtech-flight

# Create virtual environment and activate it
>$ python -m venv venv
>$ source venv/bin/activate

#  Install dependencies
>$ pip install -r requirements.txt

# Apply the migrations
>$ python manage.py migrate

# Create a .env file at the root of the application
>$ touch .env
Copy the content of .env.example file into the .env file created and supply the appropriate values for each key

# Start the application
>$ python manage.py runserver

# Open two terminal windows and run the following commands in each to start celery worker and beat. Ensure you are at the project root in each terminal with the project's virtual environment activated.
First terminal:
>$ celery -A api worker -l info

Second terminal:
>$ celery -A api beat -l info
```

## API Documentation
The API documentation can be found [here](https://documenter.getpostman.com/view/4545805/S1EJY1y2)

## Running the tests
* Create a virtual environment and activate it with the commands(this is done from the root of the application):  
```
   > $ python3 -m venv venv
   > $ source venv/bin/activate
```
* Install the dependencies with the command:  
`> $ pip install -r requirements.txt`
* Set the following environment variables in the .env file:  
  * DJANGO_ENV=development
  * SECRETE_KEY=your_secret

* Run the test with the command  
`> $ coverage run manage.py test`

* Check the coverage report with the command  
`> $ coverage report`

## Built with
* Django
* Django REST framework
* Postgresql
* Celery
* RabbitMQ

## License
This project is available for use and modification under the MIT License. See the LICENSE file or click [here](https://github.com/Dheavyman/airtech-flight/blob/develop/LICENSE.md) for more details.

## Credits
Justin Nebo
