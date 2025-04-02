from django.urls import path
from .views import (
    HomePageView, CarDetailView,
    AboutUsView, ContactUsView, RentalHistoryView, TransactionHistoryView, ActiveRentalsView, CarListView, RentCarView,
    retailer_tracking_dashboard, retailer_car_tracking_history, api_car_tracking, api_add_car_tracking,
    retailers_dashboard, checkout_view, create_payment_intent
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("cars/type/<str:type>/", CarListView.as_view(), name="car_type_list"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("about/", AboutUsView.as_view(), name="about"),
    path("contact/", ContactUsView.as_view(), name="contact"),
    path('rental-history/', RentalHistoryView.as_view(), name='rental_history'),
    path('payment-history/', TransactionHistoryView.as_view(), name='payment_history'),
    path('my-rentals/', ActiveRentalsView.as_view(), name='active_rentals'),
    path('cars/', CarListView.as_view(), name='car_list'),
    path('retailer/tracking/<int:retailer_id>/', retailer_tracking_dashboard, name='retailer_tracking_dashboard'),
    path('retailer/tracking/history/<int:retailer_id>/<int:car_id>/', retailer_car_tracking_history,
         name='retailer_car_tracking_history'),
    path('api/car_tracking/<int:retailer_id>/<int:car_id>/', api_car_tracking, name='api_car_tracking'),
    path('api/car_tracking/add/<int:retailer_id>/<int:car_id>/', api_add_car_tracking, name='api_add_car_tracking'),
    path('retailers/', retailers_dashboard, name='retailers_dashboard'),
    path("car_rent/<int:car_id>/", checkout_view, name="car_rent"),
    path("create-payment-intent/", create_payment_intent, name="create-payment-intent"),
]
