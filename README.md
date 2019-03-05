# airtech-flight
Airtech-flight is an application for managing flight booking system.

## Application features
* Users can create an account
* Users can book tickets
* Users can receive tickets as an email
* Users can check the status of their flight
* Users can make flight reservations
* Users can purchase tickets

## Prerequisites
* Install python(version 3.6 and above) and Postgresql database locally

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

# Start the application
>$ python manage.py runserver
```

## API Documentation
This will be updated as soon as the APIs are available

## Built with
* Django
* Django REST framework
* Postgresql

## Contributing to the project
Contributions are welcome and appreciated. To contribute

- Fork this repository or clone the repository with the command  
`$ git clone https://github.com/Dheavyman/airtech-flight.git`
- Change directory into the folder with the command  
`cd airtech-flight`
- Create your feature branch and make your contributions to your local copy of the project
- Raise a pull Request against the develop branch describing what your feature does and how it can be tested

## Licence
This project is available for use and modification under the MIT License. See the LICENSE file or click [here](https://github.com/Dheavyman/airtech-flight/blob/develop/LICENSE.md) for more details.
