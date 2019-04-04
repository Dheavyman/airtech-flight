from django.urls import path

from .views import BookingListView, BookingDetailView

urlpatterns = [
    path('bookings', BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:booking_pk>', BookingDetailView.as_view(), name='booking_detail')
]
