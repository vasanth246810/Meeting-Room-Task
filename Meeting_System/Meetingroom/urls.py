from django.urls import path
from .views import *

urlpatterns = [
    path("meeting-rooms/<int:room_id>/book/", MeetingRoomBookView.as_view(), name="meeting-room-book"),
    path("meeting-rooms/available/", AvailableRoomsView.as_view(), name="available-rooms"),
    path("meeting-rooms/", MeetingRoomView.as_view(), name="meeting-room-list"),
    path("bookings/", BookingRoomView.as_view(), name="booking-list"),
    path("bookings/<int:booking_id>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
]
