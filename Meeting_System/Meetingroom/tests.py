from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import MeetingRoom, Booking


class BookingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.room = MeetingRoom.objects.create(
            name="Test Room",
            capacity=10
        )

    def test_book_room_success(self):
        """Test successful booking"""
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        data = {
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
        }
        
        response = self.client.post(
            f'/api/v1/meeting-rooms/{self.room.id}/book/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_list_available_rooms(self):
        """Test listing available rooms"""
        response = self.client.get('/api/v1/meeting-rooms/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)