from django import forms
from .models import Rental
from django.utils.timezone import now

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = [
            "full_name", "phone_number", "address", "city",
            "pickup_location", "pickup_date", "pickup_time",
            "dropoff_location", "dropoff_date", "dropoff_time",
            "payment_method", "card_number", "expiration_date", "card_holder", "cvc"
        ]
        widgets = {
            "pickup_date": forms.DateInput(attrs={"type": "date"}),
            "pickup_time": forms.TimeInput(attrs={"type": "time"}),
            "dropoff_date": forms.DateInput(attrs={"type": "date"}),
            "dropoff_time": forms.TimeInput(attrs={"type": "time"}),
            "card_number": forms.TextInput(attrs={"placeholder": "1234 5678 9012 3456"}),
            "expiration_date": forms.TextInput(attrs={"placeholder": "MM/YY"}),
            "cvc": forms.TextInput(attrs={"placeholder": "123"}),
        }
