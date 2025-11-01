from rest_framework import serializers
from .models import Bus , Booking, Seat
from django.contrib.auth.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        return user

class SeatSerializer(serializers.ModelSerializer):
    price=serializers.DecimalField(source='bus.price', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_available','price']


class busSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True) 

    class Meta:
        model = Bus
        fields = ['id','bus_name', 'bus_number', 'origin', 'destination', 'features', 'start_time', 'end_time', 'no_of_seats', 'price', 'seats']

class BusSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['bus_name', 'bus_number', 'origin', 'destination','start_time','end_time','price']

class BookingSerializer(serializers.ModelSerializer):
    # bus = serializers.StringRelatedField()
    # seat = SeatSerializer
    # user = serializers.StringRelatedField()
    bus = BusSummarySerializer(read_only=True)
    seat = SeatSerializer(read_only=True)
    user = serializers.StringRelatedField()
    price = serializers.StringRelatedField()
    origin = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()


    class Meta:
        model = Booking
        fields = '__all__'
        # read_only_fields = ['user', 'booking_time', 'bus', 'seat']
        read_only_fields = ['user', 'booking_time', 'bus', 'seat', 'price','origin','destination','start_time','end_time']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_staff',
            'is_superuser',
        ]
