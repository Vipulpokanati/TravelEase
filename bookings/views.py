from django.contrib.auth import authenticate as Authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token 
from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from.serializers import UserRegisterSerializer, busSerializer, SeatSerializer, BookingSerializer

from .models import Bus, Seat, Booking
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

class Bookingview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        seat_id = request.data.get('seat')

        try:
            seat = Seat.objects.get(id=seat_id)

            if not seat.is_available:
                return Response({'error': 'Seat is already booked'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark the seat as booked
            seat.is_available = False
            seat.save()

            # Create the booking
            booking = Booking.objects.create(
                user=request.user,
                bus=seat.bus,
                seat=seat
            )

            serializer = BookingSerializer(booking)
            return Response({
                'message': 'Seat booked successfully!',
                'booking': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Seat.DoesNotExist:
            return Response({'error': 'Seat does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class UserBookingsView(APIView):   
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
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

