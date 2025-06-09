from django import forms
from .models import Rental, CarReview
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


class CarReviewForm(forms.ModelForm):
    """
    Форма для добавления отзыва к автомобилю.
    """
    class Meta:
        model = CarReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'textarea textarea-bordered w-full',
                    'placeholder': 'Расскажите о ваших впечатлениях от автомобиля, его состоянии и качестве сервиса...',
                    'rows': 4
                }
            ),
            # Мы не определяем виджет для поля 'rating', потому что в HTML-шаблоне
            # для него используется специальная верстка со звездами (на базе radio-кнопок).
            # Django корректно получит значение из поля с атрибутом name="rating".
        }

