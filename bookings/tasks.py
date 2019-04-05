import os
from datetime import timedelta

from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from api.helpers.utils import StatusChoices
from .models import Booking

@shared_task
def email_ticket(ticket):
    flight_destination = ticket['flight']['destination_airport']
    subject = f'eTicket - Flight to {flight_destination}'
    from_email = settings.EMAIL_HOST_USER
    to_email = ticket['passenger']['email']

    html_content = render_to_string('bookings/ticket.html', { 'ticket': ticket })
    text_content = strip_tags(html_content)

    message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    message.attach_alternative(html_content, 'text/html')
    message.send()

@shared_task
def email_reservation(ticket):
    flight_destination = ticket['flight']['destination']
    subject = f'eTicket - Flight to {flight_destination} Reserved'
    from_email = settings.EMAIL_HOST_USER
    to_email = ticket['passenger']['email']

    html_content = render_to_string('bookings/confirmation.html', { 'ticket': ticket })
    text_content = strip_tags(html_content)

    message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    message.attach_alternative(html_content, 'text/html')
    message.send()

@periodic_task(
    name='email_travel_reminder',
    run_every=crontab(minute=0, hour=7), # 07:00 AM every day
    ignore_result=True
)
def email_travel_reminder():
    min_threshold = timezone.now() + timedelta(days=1)
    max_threshold = timezone.now() + timedelta(days=2)

    bookings = Booking.objects.filter(Q(flight_id__departure_datetime__gt=min_threshold) &
                                      Q(flight_id__departure_datetime__lt=max_threshold),
                                      flight_status=StatusChoices.R.name)
    for booking in bookings:
        subject = f'Reminder - Flight schedule to {booking.flight_id.destination}'
        from_email = settings.EMAIL_HOST_USER
        to_email = booking.passenger_id.email

        html_content = render_to_string('bookings/reminder.html', {
            'ticket_number': booking.ticket_number,
            'departure_datetime': booking.flight_id.departure_datetime,
            'departure_airport': booking.flight_id.departing,
            'arrival_datetime': booking.flight_id.arrival_datetime,
            'destination_airport': booking.flight_id.destination,
            'passenger': [booking.passenger_id.first_name, booking.passenger_id.last_name]
        })
        text_content = strip_tags(html_content)

        message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        message.attach_alternative(html_content, 'text/html')
        message.send()
