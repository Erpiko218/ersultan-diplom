from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView, CreateView
from django.contrib import messages

from .admin import RentalForm
from .models import Car, CarReview, Rental, Transaction


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.filter(is_available=True)[:5]
        context["total_cars"] = Car.objects.count()
        context["total_brands"] = Car.objects.values("brand").distinct().count()
        context["total_reviews"] = CarReview.objects.count()
        return context


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        """Фильтруем машины по типу, если параметр передан"""
        car_type = self.request.GET.get('type')  # Исправляем на GET параметр
        if car_type:
            return Car.objects.filter(type=car_type, is_available=True)
        return Car.objects.filter(is_available=True)

    def get_context_data(self, **kwargs):
        """Добавляем активный фильтр в контекст"""
        context = super().get_context_data(**kwargs)
        context['active_filter'] = self.request.GET.get('type', 'all')
        return context


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущий автомобиль
        current_car = self.get_object()

        # Получаем список автомобилей того же типа (исключая текущий)
        related_cars = Car.objects.filter(
            type=current_car.type,
            is_available=True
        ).exclude(id=current_car.id)[:3]  # Ограничиваем до 3 машин

        context['related_cars'] = related_cars
        return context


class RentCarView(LoginRequiredMixin, CreateView):
    model = Rental
    form_class = RentalForm
    template_name = "rental/rent_car.html"
    success_url = reverse_lazy("rental_success")  # редирект после успешной аренды

    def form_valid(self, form):
        rental = form.save(commit=False)
        rental.user = self.request.user

        # Проверка заполнения данных карты, если выбрана оплата картой
        if rental.payment_method == "CARD":
            if not (rental.card_number and rental.expiration_date and rental.card_holder and rental.cvc):
                messages.error(self.request, "Заполните данные карты!")
                return self.form_invalid(form)

        rental.save()
        messages.success(self.request, "Аренда успешно оформлена!")
        return super().form_valid(form)


class ContactUsView(TemplateView):
    template_name = "contact.html"


class AboutUsView(TemplateView):
    template_name = "about.html"


class RentalHistoryView(ListView):
    model = Rental
    template_name = 'rental_history.html'
    context_object_name = 'rentals'

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user).order_by('-end_date')


class TransactionHistoryView(ListView):
    model = Transaction
    template_name = 'payment_history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')


class ActiveRentalsView(ListView):
    model = Rental
    template_name = 'cars/active_rentals.html'
    context_object_name = 'rentals'

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user, is_active=True)

