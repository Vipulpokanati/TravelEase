from django.contrib.auth import authenticate as Authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token 
from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from.serializers import UserRegisterSerializer, busSerializer, SeatSerializer, BookingSerializer
from django.db import transaction
import shortuuid
from .models import Bus, Seat, Booking
from django.db.models import Prefetch

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Loginview(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = Authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class BusListCreateView(generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = busSerializer

class BusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bus.objects.all()
    serializer_class = busSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Seat, Booking, Bus
import uuid

class Bookingview(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        bus_id = request.data.get("bus_id")
        seat_numbers = request.data.get("seats", [])

        # Validate input
        if not bus_id:
            return Response({"error": "Please provide bus_id."}, status=status.HTTP_400_BAD_REQUEST)

        if not seat_numbers or not isinstance(seat_numbers, list):
            return Response({"error": "Please provide a list of seat numbers."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the bus
        try:
            bus = Bus.objects.get(id=bus_id)
        except Bus.DoesNotExist:
            return Response({"error": "Bus not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch seats for this bus
        seats = Seat.objects.filter(bus=bus, seat_number__in=seat_numbers, is_available=True)

        # Check if all requested seats exist and are available
        if len(seats) != len(seat_numbers):
            return Response({"error": "One or more seats do not exist or are already booked."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate a single ticket ID for this booking
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"

        bookings = []
        for seat in seats:
            seat.is_available = False
            seat.save()
            booking = Booking.objects.create(
                ticket_id=ticket_id,
                user=request.user,
                bus=bus,
                seat=seat
            )
            bookings.append(booking)

        seat_list = [b.seat.seat_number for b in bookings]
        total_price = bus.price * len(seat_list)

        return Response({
            "message": f"{len(bookings)} seat(s) booked successfully!",
            "ticket_id": ticket_id,
            "bus_name": bus.bus_name,
            "bus_number": bus.bus_number,
            "seats": seat_list,
            "origin": bus.origin,
            "destination": bus.destination,
            "price_per_seat": f"{bus.price:.2f}",
            "total_price": f"{total_price:.2f}",
            "booking_time": bookings[0].booking_time,
        }, status=status.HTTP_201_CREATED)

class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
<<<<<<< HEAD
            return Response({'error': 'You are not authorized to view these bookings.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        bookings = Booking.objects.filter(user_id=user_id).select_related('bus', 'seat')

        if not bookings.exists():
            return Response({'message': 'No bookings found.'}, status=status.HTTP_200_OK)

        # Group bookings by ticket_id
        grouped = {}
        for b in bookings:
            tid = b.ticket_id
            if tid not in grouped:
                grouped[tid] = {
                    "ticket_id": tid,
                    "bus_name": b.bus.bus_name,
                    "bus_number": b.bus.bus_number,
                    "origin": b.bus.origin,
                    "destination": b.bus.destination,
                    "price_per_seat": f"{b.bus.price:.2f}",
                    "seats": [],
                    "booking_time": b.booking_time,
                }
            grouped[tid]["seats"].append(b.seat.seat_number)

        # Compute total price
        for t in grouped.values():
            t["total_price"] = f"{float(t['price_per_seat']) * len(t['seats']):.2f}"

        return Response(list(grouped.values()), status=status.HTTP_200_OK)
=======
            return Response({'error': 'You are not authorized to view these bookings.'}, status=status.HTTP_401_UNAUTHORIZED)
        bookings = Booking.objects.filter(user_id=user_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserSerializer
>>>>>>> 34f913c8938be3bddac076e59c37b2fc48d0f3df

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            # Only allow users to view their own details (unless admin)
            if request.user.id != user_id and not request.user.is_staff:
                return Response(
                    {"error": "You are not authorized to view this user's details."},
                    status=status.HTTP_403_FORBIDDEN
                )

            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

