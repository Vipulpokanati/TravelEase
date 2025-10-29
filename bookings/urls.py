from .views import RegisterView, Loginview, BusListCreateView, BusDetailView, Bookingview, UserBookingsView, UserDetailView
from django.urls import path

urlpatterns = [
    path('buses/', BusListCreateView.as_view(), name='buslist'),
    path('buses/<int:pk>/', BusDetailView.as_view(), name='bus-detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', Loginview.as_view(), name='login'),  
    path('user/<int:user_id>/bookings/', UserBookingsView.as_view(), name='user-bookings'),
    path('bookings/', Bookingview.as_view(), name='bookings'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
]
