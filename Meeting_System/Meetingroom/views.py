from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_datetime
from .models import MeetingRoom, Booking, History
from .serializers import AvailableRoomSerializer, MeetingRoomSerializer, BookingSerializer ,BookingCreateSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction



class MeetingRoomView(ListAPIView):
    serializer_class=MeetingRoomSerializer
    queryset=MeetingRoom.objects.filter(is_active=True)

class BookingRoomView(ListAPIView):
    serializer_class=BookingSerializer
    queryset=Booking.objects.all()

class MeetingRoomBookView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, room_id):
        try:
            room = get_object_or_404(MeetingRoom, id=room_id)
            if not room.is_active:
                return Response({"error": "Meeting room is not active"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BookingCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            start_time = serializer.validated_data["start_time"]
            end_time = serializer.validated_data["end_time"]
            purpose = serializer.validated_data.get("purpose", "")
            if not room.is_available(start_time, end_time):
                return Response(
                    {
                        "error": "Meeting room is not available for the selected time slot",
                        "room_id": room_id,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                    },status=status.HTTP_409_CONFLICT,)
            booking_data = {
                "meeting_room": room.id,
                "start_time": start_time,
                "end_time": end_time,
                "purpose": purpose,
                "status": "confirmed",
            }
            booking_serializer = BookingSerializer(data=booking_data, context={"request": request})
            if not booking_serializer.is_valid():
                return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            booking_serializer.save()
            return Response(
                {"message": "Booking created successfully", "booking": booking_serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except MeetingRoom.DoesNotExist:
            return Response({"error": "Meeting room not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableRoomsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            start_time_str = request.query_params.get('start_time')
            end_time_str = request.query_params.get('end_time')
            rooms = MeetingRoom.objects.filter(is_active=True)
            if start_time_str and end_time_str:
                start_time = parse_datetime(start_time_str)
                end_time = parse_datetime(end_time_str)
                if not start_time or not end_time:
                    return Response({"error": "Invalid datetime format. Use ISO 8601 (e.g., 2026-01-28T10:00:00Z)"}, status=status.HTTP_400_BAD_REQUEST)
                if start_time >= end_time:
                    return Response({"error": "End time must be after start time"}, status=status.HTTP_400_BAD_REQUEST)
                booked = Booking.objects.filter(status__in=["confirmed", "pending"],start_time__lt=end_time,end_time__gt=start_time).values_list("meeting_room_id", flat=True)
                available_rooms = rooms.exclude(id__in=booked)
                serializer = AvailableRoomSerializer(available_rooms, many=True)
                return Response({
                    "available_rooms": serializer.data,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "count": len(available_rooms)
                }, status=status.HTTP_200_OK)
            else:
                serializer = AvailableRoomSerializer(rooms, many=True)
                return Response({"available_rooms": serializer.data,"count": rooms.count()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingCancelView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request, booking_id):
        try:
            booking = get_object_or_404(Booking, id=booking_id)
            if booking.status == 'cancelled':
                return Response({'error': 'Booking already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
            previous_start = booking.start_time
            previous_end = booking.end_time
            booking.status = 'cancelled'
            booking.save()
            History.objects.create(
                booking=booking,
                action='cancelled',
                user=None,
                notes='Cancelled via API',
                previous_start_time=previous_start,
                previous_end_time=previous_end
            )
            return Response({'message': 'Booking cancelled successfully'}, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

