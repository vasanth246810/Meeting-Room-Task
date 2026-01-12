from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class MeetingRoom(models.Model):
    """Model representing a meeting room"""
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"

    def is_available(self, start_time, end_time):
        """Check if the room is available for the given time range"""
        overlapping_bookings = self.bookings.filter(
            status__in=['confirmed', 'pending'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        return not overlapping_bookings.exists()


class Booking(models.Model):
    """Model representing a meeting room booking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    meeting_room = models.ForeignKey(
        MeetingRoom, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        null=True,
        blank=True
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='confirmed'
    )
    purpose = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.meeting_room.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate booking times"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("End time must be after start time")
            
            if self.start_time < timezone.now():
                raise ValidationError("Cannot book in the past")
            
            # Check for overlapping bookings
            if self.meeting_room:
                overlapping = Booking.objects.filter(
                    meeting_room=self.meeting_room,
                    status__in=['confirmed', 'pending'],
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time
                ).exclude(pk=self.pk)
                
                if overlapping.exists():
                    raise ValidationError(
                        "This room is already booked for the selected time"
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class History(models.Model):
    """Model for tracking booking history and changes"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('cancelled', 'Cancelled'),
    ]

    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    previous_start_time = models.DateTimeField(null=True, blank=True)
    previous_end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Histories'

    def __str__(self):
        return f"{self.action} - {self.booking} at {self.timestamp}"