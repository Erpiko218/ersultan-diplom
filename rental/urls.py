from django.urls import path
from .views import (
    HomePageView, CarDetailView,
    AboutUsView, ContactUsView, RentalHistoryView, TransactionHistoryView, ActiveRentalsView, CarListView, RentCarView
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("cars/type/<str:type>/", CarListView.as_view(), name="car_type_list"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("cars/<int:pk>/rent/", RentCarView.as_view(), name="car_rent"),
    path("about/", AboutUsView.as_view(), name="about"),
    path("contact/", ContactUsView.as_view(), name="contact"),
    path('rental-history/', RentalHistoryView.as_view(), name='rental_history'),
    path('payment-history/', TransactionHistoryView.as_view(), name='payment_history'),
    path('my-rentals/', ActiveRentalsView.as_view(), name='active_rentals'),
    path('cars/', CarListView.as_view(), name='car_list'),
]
