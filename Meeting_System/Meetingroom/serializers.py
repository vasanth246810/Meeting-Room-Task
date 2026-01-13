from rest_framework import serializers
from django.utils import timezone
from .models import MeetingRoom, Booking, History


class MeetingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = ['id', 'name', 'capacity', 'description', 'is_active']


class HistorySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = [
            'id', 'action', 'user_name', 'timestamp', 
            'notes', 'previous_start_time', 'previous_end_time'
        ]

    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'System'


class BookingSerializer(serializers.ModelSerializer):
    meeting_room_name = serializers.CharField(
        source='meeting_room.name', 
        read_only=True
    )
    user_name = serializers.SerializerMethodField()
    history = HistorySerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'meeting_room', 'meeting_room_name', 'user', 'user_name',
            'start_time', 'end_time', 'status', 'purpose', 
            'created_at', 'updated_at', 'history'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anonymous'

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        meeting_room = data.get('meeting_room')

        # Validate time range
        if start_time >= end_time:
            raise serializers.ValidationError(
                "End time must be after start time"
            )

        # Validate not in the past
        if start_time < timezone.now():
            raise serializers.ValidationError(
                "Cannot book in the past"
            )

        # Check room availability
        if meeting_room:
            overlapping = Booking.objects.filter(
                meeting_room=meeting_room,
                status__in=['confirmed', 'pending'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Exclude current booking if updating
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            if overlapping.exists():
                raise serializers.ValidationError(
                    "This room is already booked for the selected time"
                )

        return data

    def create(self, validated_data):
        # Set user from context if available
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        booking = super().create(validated_data)
        
        # Create history entry
        History.objects.create(
            booking=booking,
            action='created',
            user=validated_data.get('user'),
            notes='Booking created'
        )
        
        return booking


class BookingCreateSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    purpose = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time >= end_time:
            raise serializers.ValidationError(
                "End time must be after start time"
            )

        if start_time < timezone.now():
            raise serializers.ValidationError(
                "Cannot book in the past"
            )

        return data


class AvailableRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = ['id', 'name', 'capacity', 'description']