import io
import json
from datetime import timezone, datetime, timedelta
from time import timezone

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, ListView, CreateView
from django.contrib import messages
from fpdf import FPDF

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


class ContactUsView(TemplateView):
    template_name = "contact.html"


class AboutUsView(TemplateView):
    template_name = "about.html"


class RentalDetailView(LoginRequiredMixin, DetailView):
    model = Rental
    template_name = "rental_detail.html"
    context_object_name = "rental"

    def get_queryset(self):
        # Ограничиваем выборку аренд только текущим пользователем
        return Rental.objects.filter(user=self.request.user)


class TransactionHistoryView(ListView):
    model = Transaction
    template_name = 'payment_history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-timestamp')


class MyRentalsView(LoginRequiredMixin, TemplateView):
    template_name = 'active_rentals.html'  # Можно назвать, например, my_rentals.html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Активные аренды – например, аренды, которые оплачены и имеют статус COMPLETED
        context['active_rentals'] = Rental.objects.filter(user=self.request.user, is_paid=True, status="OWNED")
        # История (неактивные аренды) – аренды, которые не имеют статус COMPLETED
        context['inactive_rentals'] = Rental.objects.filter(user=self.request.user).exclude(status="COMPLETED")
        return context


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


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout_view(request, car_id):
    """
    Создаёт запись Rental с placeholder-данными (is_paid=False) и передаёт rental_id в шаблон.
    При дальнейшей обработке заполнение данных можно обновить.
    """
    car = get_object_or_404(Car, id=car_id)

    # Заполняем placeholder-данными необходимые поля
    now = datetime.now()
    today = now.date()
    dummy_time = now.time().replace(hour=0, minute=0, second=0, microsecond=0)

    rental = Rental.objects.create(
        user=request.user,
        car=car,
        start_time=now,
        end_time=now + timedelta(hours=24),  # placeholder – аренда на 1 день
        full_name=request.user.get_full_name() or request.user.username,
        phone_number="",
        address="",
        city="",
        pickup_location="",
        pickup_date=today,
        pickup_time=dummy_time,
        dropoff_location="",
        dropoff_date=today,
        dropoff_time=dummy_time,
        payment_method="CARD",
        is_paid=False,
        total_price=car.price_per_day  # placeholder, можно пересчитать по нужной логике
    )

    return render(request, "rent_car.html", {
        "car": car,
        "stripe_pk": settings.STRIPE_PUBLISHABLE_KEY,
        "rental_id": rental.id,
    })

@csrf_exempt
@login_required
def update_rental(request):
    """
    Обновляет данные Rental, полученные из формы.
    Ожидается POST-запрос с данными и rental_id.
    """
    if request.method == "POST":
        rental_id = request.POST.get("rental_id")
        rental = get_object_or_404(Rental, id=rental_id, user=request.user)
        rental.full_name = request.POST.get("full_name", rental.full_name)
        rental.phone_number = request.POST.get("phone_number", rental.phone_number)
        rental.address = request.POST.get("address", rental.address)
        rental.city = request.POST.get("city", rental.city)
        rental.pickup_location = request.POST.get("pickup_location", rental.pickup_location)
        rental.pickup_date = request.POST.get("pickup_date", rental.pickup_date)
        rental.pickup_time = request.POST.get("pickup_time", rental.pickup_time)
        rental.dropoff_location = request.POST.get("dropoff_location", rental.dropoff_location)
        rental.dropoff_date = request.POST.get("dropoff_date", rental.dropoff_date)
        rental.dropoff_time = request.POST.get("dropoff_time", rental.dropoff_time)
        rental.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Метод не разрешен"}, status=405)


@csrf_exempt
def create_payment_intent(request):
    """
    Создаёт PaymentIntent и передаёт rental_id в metadata.
    Ожидает JSON с полями: amount (сумма в USD, например, цена за день) и rental_id.
    """
    data = json.loads(request.body)
    amount = data.get("amount")
    rental_id = data.get("rental_id")

    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),  # переводим сумму в центы
        currency="usd",
        automatic_payment_methods={"enabled": True},
        metadata={"rental_id": rental_id}
    )
    return JsonResponse({"clientSecret": intent.client_secret})


@login_required
def processing_view(request):
    rental_id = request.GET.get("rental_id")
    if not rental_id:
        return HttpResponseForbidden("Rental ID не передан")
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    return render(request, "processing.html", {"rental": rental})


@login_required
def check_transaction(request):
    """
    Возвращает статус аренды по rental_id: "success" если rental.is_paid True, иначе "processing".
    """
    rental_id = request.GET.get("rental_id")
    if not rental_id:
        return JsonResponse({"error": "Rental ID required"}, status=400)

    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if settings.DEBUG:
        return JsonResponse({"status": "success"})
    if rental.is_paid:
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "processing"})


# Страница подтверждения аренды с информацией о машине, дилере и картой (центр карты — Астана)
@login_required
def rental_success(request):
    rental_id = request.GET.get("rental_id")
    if not rental_id:
        return HttpResponseForbidden("Rental ID не передан")
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if settings.DEBUG:
        rental.is_paid = True
        rental.status = "OWNED"
        rental.save()

    return render(request, "rental_success.html", {"rental": rental})


@login_required
def download_receipt(request):
    rental_id = request.GET.get("rental_id")
    if not rental_id:
        return HttpResponseForbidden("Rental ID не передан")
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)

    pdf = FPDF()
    pdf.add_page()

    # Заголовок
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Квитанция по аренде", ln=True, align="C")
    pdf.ln(5)

    # Детали аренды
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"ID аренды: {rental.id}", ln=True)
    pdf.cell(0, 10, f"Автомобиль: {rental.car.brand} {rental.car.model}", ln=True)

    dealer_name = rental.car.dealer.name if rental.car.dealer else "Не указан"
    pdf.cell(0, 10, f"Дилер: {dealer_name}", ln=True)

    pdf.cell(0, 10, f"Дата получения: {rental.pickup_date} {rental.pickup_time}", ln=True)
    pdf.cell(0, 10, f"Дата возврата: {rental.dropoff_date} {rental.dropoff_time}", ln=True)
    pdf.cell(0, 10, f"Итоговая цена: {rental.total_price}", ln=True)
    pdf.cell(0, 10, f"Оплачено: {'Да' if rental.is_paid else 'Нет'}", ln=True)

    # Получаем PDF в виде строки байт
    pdf_output = pdf.output(dest="S").encode("latin1")

    response = HttpResponse(pdf_output, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_rental_{rental.id}.pdf'
    return response


@csrf_exempt
def stripe_webhook(request):
    """
    Обрабатывает события Stripe.
    При событии payment_intent.succeeded обновляет rental.is_paid на True.
    При payment_intent.payment_failed оставляет is_paid=False.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET  # настройте в settings.py
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        rental_id = intent.get("metadata", {}).get("rental_id")
        if rental_id:
            try:
                rental = Rental.objects.get(id=rental_id)
                rental.is_paid = True
                rental.status = "OWNED"
                rental.save()
            except Rental.DoesNotExist:
                pass
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        rental_id = intent.get("metadata", {}).get("rental_id")
        if rental_id:
            try:
                rental = Rental.objects.get(id=rental_id)
                rental.is_paid = False
                rental.status = "REJECTED"
                rental.save()
            except Rental.DoesNotExist:
                pass

    return HttpResponse(status=200)
