from django.urls import path
from .views import MeetingView, AvaliableRoomsView, MeetingRoomView, BookingRoomView

urlpatterns = [
    # Required endpoints
    path(
        'meeting-rooms/<int:room_id>/book/',
        MeetingView.as_view(),
        name='meeting-room-book'
    ),
    path(
        'meeting-rooms/available/',
        AvaliableRoomsView.as_view(),
        name='available-rooms'
    ),
    
    # Additional endpoints
    path(
        'meeting-rooms/',
        MeetingRoomView.as_view(),
        name='meeting-room-list'
    ),
    path(
        'bookings/',
        BookingRoomView.as_view(),
        name='booking-list'
    ),
]