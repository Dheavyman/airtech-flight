import os

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def email_ticket(ticket):
    flight_destination = ticket['flight']['destination_airport']
    subject = f'eTicket - Flight to {flight_destination}'
    from_email = settings.EMAIL_HOST_USER
    to_email = ticket['passenger']['email']

    content_html = render_to_string('bookings/ticket.html', { 'ticket': ticket})
    content_text = strip_tags(content_html)

    message = EmailMultiAlternatives(subject, content_text, from_email, [to_email])
    message.attach_alternative(content_html, 'text/html')
    message.send()
