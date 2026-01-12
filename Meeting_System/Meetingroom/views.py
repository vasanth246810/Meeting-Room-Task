from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from .models import MeetingRoom, Booking
from .serializers import AvailableRoomSerializer, MeetingRoomSerializer, BookingSerializer 

class MeetingView(APIView):
    def post(self,room_id,request):
        try:
            room=MeetingRoom.objects.get(id=room_id)
            if not room.is_active:
                return Response({"error": "Meeting room is not active."}, status=status.HTTP_400_BAD_REQUEST)
            serializer=BookingSerializer(data=request.data)
            if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            start_time=serializer.validated_data['start_time']
            end_time=serializer.validated_data['end_time']
            purpose=serializer.validated_data['purpose']
            if not room.is_avaliable(start_time,end_time):
                return Response(
                    {"error": "Meeting room is not available for the selected time slot.",
                                'room_id':room_id,
                                'start_time':start_time,
                                'end_time':end_time}, 
                            status=status.HTTP_400_BAD_REQUEST)
            booking_data={
                'meetingroom':room,
                'start_time':start_time,
                'end_time':end_time,
                'purpose':purpose
            }
            booking_serializer=BookingSerializer(data=booking_data)
            if booking_serializer.is_valid():
                booking_serializer.save()
                return Response("Booking created successfully", status=status.HTTP_201_CREATED)
            else:
                return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    


class AvaliableRoomsView(APIView):
    def get(self,request):
        try:
            start_time=parse_datetime(request.query_params.get('start_time'))
            end_time=parse_datetime(request.query_params.get('end_time'))
            rooms=MeetingRoom.objects.filter(is_active=True)
            if start_time and end_time:
                try:
                    if start_time >= end_time:
                        return Response({"error": "End time must be after start time."}, status=status.HTTP_400_BAD_REQUEST)
                    avaliable_rooms=[]
                    for room in rooms:
                        if room.is_avaliable(start_time,end_time):
                            avaliable_rooms.append(room)
                    serializer=AvailableRoomSerializer(avaliable_rooms,many=True)
                    return Response({
                        "avaliable_rooms":serializer.data,
                        "start_time":start_time,
                        "end_time":end_time,
                        "Count":len(avaliable_rooms)
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer=AvailableRoomSerializer(avaliable_rooms,many=True)
                return Response({
                    "avaliable_rooms":serializer.data,
                    "Count":rooms.count()
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MeetingRoomView(ListAPIView):
    serializer_class=MeetingRoomSerializer
    queryset=MeetingRoom.objects.filter(is_active=True)

class BookingRoomView(ListAPIView):
    serializer_class=BookingSerializer
    queryset=Booking.objects.all()

