from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("cars/<int:pk>/", car_detail, name="car_detail"),
    path("about/", AboutUsView.as_view(), name="about"),
    path("contact/", ContactUsView.as_view(), name="contact"),
    path('rental-history/', MyRentalsView.as_view(), name='rental_history'),
    path('payment-history/', TransactionHistoryView.as_view(), name='payment_history'),
    path('rental/<int:pk>', RentalDetailView.as_view(), name="rental_detail"),
    path('cars/', car_list, name='car_list'),
    path('retailer/tracking/<int:retailer_id>/', retailer_tracking_dashboard, name='retailer_tracking_dashboard'),
    path('retailer/tracking/history/<int:retailer_id>/<int:car_id>/', retailer_car_tracking_history,
         name='retailer_car_tracking_history'),
    path('api/car_tracking/<int:retailer_id>/<int:car_id>/', api_car_tracking, name='api_car_tracking'),
    path('api/car_tracking/add/<int:retailer_id>/<int:car_id>/', api_add_car_tracking, name='api_add_car_tracking'),
    path('retailers/', retailers_dashboard, name='retailers_dashboard'),
    path("car_rent/<int:car_id>/", checkout_view, name="car_rent"),
    path("create-payment-intent/", create_payment_intent, name="create-payment-intent"),
    path("processing/", processing_view, name="processing"),
    path("check-transaction/", check_transaction, name="check_transaction"),
    path("rental-success/", rental_success, name="rental_success"),
    path("download-receipt/", download_receipt_docx, name="download_receipt"),
    path("stripe-webhook/", stripe_webhook, name="stripe_webhook"),
    path("update-rental/", update_rental, name="update_rental"),

    path("search_suggestions/", search_suggestions, name="search_suggestions"),
    path("notifications/", notifications_page, name="notifications"),
    path("notifications/dropdown/", notifications_dropdown,
         name="notifications_dropdown"),
    path("favorites/", favorites, name="favorites"),
    path('cars/<int:pk>/favorite-toggle/', favorite_toggle, name='favorite_toggle'),

    path("search/", car_search, name="car_search"),

    path('dealers/<int:pk>/', dealer_detail, name='dealer_detail'),
    path('faq/', faq, name='faq'),


    # список всех дилеров для админа
    path(
        'control/dealers/',
        admin_dealers_list,
        name='admin_dealers_list'
    ),
    # детальная страница дилера
    path(
        'control/dealers/<int:pk>/',
        admin_dealer_detail,
        name='admin_dealer_detail'
    ),

    path('rental/<int:rental_id>/cancel/', cancel_rental_view, name='cancel_rental'),
    path('finish_rental/<int:rental_id>/', finish_rental_view, name='finish_rental'),
    path('car/<int:car_id>/confirm-inspection/', confirm_inspection_view, name='confirm_inspection'),
    path('car/<int:car_id>/reviews/', car_reviews_view, name='car_reviews'),
    path("how-it-works/", HowItWorksView.as_view(), name="how_it_works"),
    path("blog/", BlogView.as_view(), name="blog"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-of-use/", TermsOfUseView.as_view(), name="terms_of_use"),
    path("service-conditions/", ServiceConditionsView.as_view(), name="service_conditions"),
]
