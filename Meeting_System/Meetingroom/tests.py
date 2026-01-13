from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import MeetingRoom, Booking, History


class BookingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.room = MeetingRoom.objects.create(name="Test Room", capacity=10)

    def test_book_room_success(self):
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        data = {"start_time": start.isoformat(), "end_time": end.isoformat()}
        response = self.client.post(
            f"/api/v1/meeting-rooms/{self.room.id}/book/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_available_rooms(self):
        response = self.client.get("/api/v1/meeting-rooms/available/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_room_conflict(self):
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        Booking.objects.create(
            meeting_room=self.room, start_time=start, end_time=end, status="confirmed"
        )
        conflict_start = start + timedelta(minutes=30)
        conflict_end = conflict_start + timedelta(hours=1)
        data = {
            "start_time": conflict_start.isoformat(),
            "end_time": conflict_end.isoformat(),
        }
        response = self.client.post(
            f"/api/v1/meeting-rooms/{self.room.id}/book/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cancel_booking(self):
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        data = {"start_time": start.isoformat(), "end_time": end.isoformat()}
        response = self.client.post(
            f"/api/v1/meeting-rooms/{self.room.id}/book/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking_id = response.data.get("booking", {}).get("id")
        self.assertIsNotNone(booking_id)
        cancel_response = self.client.post(
            f"/api/v1/bookings/{booking_id}/cancel/", format="json"
        )
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        booking = Booking.objects.get(id=booking_id)
        self.assertEqual(booking.status, "cancelled")
        self.assertTrue(booking.history.filter(action="cancelled").exists())
