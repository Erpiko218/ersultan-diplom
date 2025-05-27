# your_app/context_processors.py
from django.conf import settings
from django.db.models import Count, Sum
from .models import Rental, Favorite


def navbar_data(request):
    """
    Данные для navbar: избранное, уведомления, роли и базовые метрики пользователя.
    """
    ctx = {}
    user = request.user

    if user.is_authenticated:
        # Избранное: первые 5 для выпадашки + общее число
        fav_qs = Favorite.objects.filter(user=user).select_related('car')
        ctx['favorites'] = fav_qs[:5]
        ctx['favorites_count'] = fav_qs.count()

        # Уведомления: число непрочитанных и пять последних
        notif_qs = user.notifications.order_by('-created_at')
        ctx['unread_notifications_count'] = notif_qs.filter(is_read=False).count()
        ctx['recent_notifications'] = notif_qs[:5]

        # Роли: дилер или суперпользователь
        ctx['is_superuser'] = user.is_superuser
        if user.retailer is not None:
            ctx['is_dealer'] = True
            ctx['dealer_id'] = user.retailer.id
        else:
            ctx['is_dealer'] = False
            ctx['dealer_id'] = None

        # Активные аренды пользователя
        ctx['active_rentals_count'] = Rental.objects.filter(
            user=user,
            status='active'
        ).count()

        # Для дилера: сводка по парку и доходам
        if ctx['is_dealer']:
            dealer = user.retailer
            cars_count = dealer.cars.count()
            active_rentals = Rental.objects.filter(
                car__dealer=dealer,
                status='active'
            ).count()
            total_revenue = Rental.objects.filter(
                car__dealer=dealer,
                status='completed'
            ).aggregate(sum=Sum('total_price'))['sum'] or 0
            ctx['dealer_stats'] = {
                'cars_count': cars_count,
                'active_rentals': active_rentals,
                'total_revenue': total_revenue,
            }

    return ctx


def filter_values(request):
    """
    Берёт из request.GET выбранные фильтры
    и отдаёт их в контекст каждого шаблона.
    """
    return {
        "selected_types":        request.GET.getlist("type"),
        "selected_transmissions": request.GET.getlist("transmission"),
        "selected_dealers":      request.GET.getlist("dealer"),
        "price_to":              request.GET.get("price_to", ""),
        "query":                 request.GET.get("q", ""),
    }


def api_keys_processor(request):
    """
    Добавляет API-ключи и другие конфигурации в контекст шаблонов.
    ВНИМАНИЕ: Ключи, доступные через этот процессор, будут видны
    в исходном коде страницы, если вы выведете их в JavaScript.
    Используйте с ОСТОРОЖНОСТЬЮ.
    """
    return {
        'GEMINI_API_KEY': getattr(settings, 'GEMINI_API_KEY', ""),
    }
