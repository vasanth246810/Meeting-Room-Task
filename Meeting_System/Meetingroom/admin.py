from django.contrib import admin
from .models import MeetingRoom, Booking, History


@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['meeting_room', 'user', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'meeting_room']
    search_fields = ['purpose']
    date_hierarchy = 'start_time'


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'action', 'user', 'timestamp']
    list_filter = ['action']
    date_hierarchy = 'timestamp'