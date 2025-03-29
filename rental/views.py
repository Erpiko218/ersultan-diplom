from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView, CreateView
from django.contrib import messages

from .admin import RentalForm
from .models import Car, CarReview, Rental, Transaction, TripTracking, CarLocation, Dealer


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


def user_is_retailer(user):
    """
    Проверяет, является ли пользователь суперпользователем или входит в группу "Retailers"
    """
    return user.is_superuser or user.groups.filter(name="Retailers").exists()


@login_required
def retailer_tracking_dashboard(request, retailer_id):
    """
    Дэшборд для просмотра трекинга машин конкретного ритейлера.
    Фильтруется по типу автомобиля и доступности, при этом выбираются
    только те машины, у которых car.dealer_id совпадает с retailer_id.
    """
    # Получаем фильтры из GET-параметров
    car_type = request.GET.get('car_type')
    is_available = request.GET.get('is_available')

    # Выбираем объекты CarLocation с подгрузкой связанных моделей и фильтруем по дилеру
    locations = CarLocation.objects.select_related('car', 'car__dealer').filter(car__dealer_id=retailer_id)
    if car_type:
        locations = locations.filter(car__type=car_type)
    if is_available:
        if is_available.lower() == 'true':
            locations = locations.filter(car__is_available=True)
        elif is_available.lower() == 'false':
            locations = locations.filter(car__is_available=False)

    # Список возможных типов автомобилей для фильтрации
    car_types = Car.CarType.choices

    context = {
        'locations': locations,
        'car_types': car_types,
        'selected_car_type': car_type,
        'selected_is_available': is_available,
        'retailer_id': retailer_id,
    }
    return render(request, 'retailer_tracking_dashboard.html', context)


@login_required
def retailer_car_tracking_history(request, retailer_id, car_id):
    """
    Страница истории трекинга для конкретной машины.
    Проверяем, что машина принадлежит ритейлеру с идентификатором retailer_id.
    """
    car = get_object_or_404(Car, id=car_id, dealer_id=retailer_id)

    # Получаем текущее местоположение машины (если оно имеется)
    try:
        location = car.location
    except CarLocation.DoesNotExist:
        location = None

    # Получаем историю трекинга (все записи по всем арендам данной машины)
    tracking_logs = TripTracking.objects.filter(rental__car=car).order_by('timestamp')

    context = {
        'car': car,
        'location': location,
        'tracking_logs': tracking_logs,
        'retailer_id': retailer_id,
    }
    return render(request, 'retailer_car_tracking_history.html', context)


@login_required
def retailers_dashboard(request):
    """
    Страница дэшборда, показывающая всех ритейлеров (дилерские центры).
    При клике на ритейлера пользователь перенаправляется на страницу
    retailer_tracking_dashboard с нужным идентификатором.
    """
    retailers = Dealer.objects.all().order_by('name')
    context = {
        'retailers': retailers,
    }
    return render(request, 'retailers_dashboard.html', context)


def api_car_tracking(request, retailer_id, car_id):
    """
    API-эндпоинт для получения данных трекинга конкретной машины,
    принадлежащей ритейлеру с идентификатором retailer_id.
    """
    car = get_object_or_404(Car, id=car_id, dealer_id=retailer_id)
    try:
        location = car.location
        loc_data = {
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'updated_at': location.updated_at.isoformat(),
        }
    except CarLocation.DoesNotExist:
        loc_data = None

    tracking_logs = TripTracking.objects.filter(rental__car=car).order_by('timestamp')
    logs_data = [
        {
            'latitude': float(log.latitude),
            'longitude': float(log.longitude),
            'timestamp': log.timestamp.isoformat(),
        }
        for log in tracking_logs
    ]
    return JsonResponse({
        'location': loc_data,
        'tracking_logs': logs_data,
    })


def api_add_car_tracking(request, retailer_id, car_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Метод не разрешен. Используйте POST.'}, status=405)

    # Проверяем, что машина принадлежит ритейлеру (dealer)
    car = get_object_or_404(Car, id=car_id, dealer_id=retailer_id)

    # Получаем rental_id из POST-данных
    rental_id = request.POST.get('rental_id')
    if not rental_id:
        return JsonResponse({'error': 'Параметр rental_id обязателен.'}, status=400)

    try:
        rental_id = int(rental_id)
    except ValueError:
        return JsonResponse({'error': 'rental_id должен быть числовым.'}, status=400)

    # Проверяем, что аренда существует для этой машины
    try:
        rental = car.rental_set.get(id=rental_id)
    except Rental.DoesNotExist:
        return JsonResponse({'error': 'Аренда с данным rental_id не найдена для этой машины.'}, status=404)

    # Получаем координаты из POST-данных
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    if latitude is None or longitude is None:
        return JsonResponse({'error': 'Параметры latitude и longitude обязательны.'}, status=400)

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return JsonResponse({'error': 'Неверный формат координат.'}, status=400)

    # Создаем новую запись трекинга
    tracking = TripTracking.objects.create(
        rental=rental,
        latitude=latitude,
        longitude=longitude
    )

    return JsonResponse({
        'status': 'success',
        'tracking': {
            'id': tracking.id,
            'latitude': float(tracking.latitude),
            'longitude': float(tracking.longitude),
            'timestamp': tracking.timestamp.isoformat(),
        }
    })
