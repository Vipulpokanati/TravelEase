from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Bus, Seat, Booking

class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_name', 'bus_number', 'origin', 'destination', 'start_time', 'end_time', 'price', 'reset_seats_button')
    search_fields = ('bus_name', 'bus_number', 'origin', 'destination')

    # Add custom URLs for actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:bus_id>/reset-seats/', self.admin_site.admin_view(self.reset_seats), name='reset-seats'),
        ]
        return custom_urls + urls

    # Action logic
    def reset_seats(self, request, bus_id):
        bus = Bus.objects.get(id=bus_id)
        bus.seats.update(is_available=True)
        self.message_user(request, f"All seats for {bus.bus_name} are now available.")
        return redirect(f'/admin/bookings/bus/{bus_id}/change/')

    # Display the button
    def reset_seats_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Reset Seats</a>',
            f'/admin/bookings/bus/{obj.id}/reset-seats/'
        )
    reset_seats_button.short_description = 'Reset Seats'
    reset_seats_button.allow_tags = True

class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'bus', 'is_available')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('ticket_id','user', 'bus', 'seat', 'booking_time', 'origin', 'destination', 'price')

admin.site.register(Bus, BusAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Booking, BookingAdmin)
