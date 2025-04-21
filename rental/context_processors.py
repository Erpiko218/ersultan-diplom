def navbar_data(request):
    if request.user.is_authenticated:
        return {
            "favorites": request.user.favorite_set.select_related('car')[:5],
            "unread_notifications_count": request.user.notifications.filter(is_read=False).count(),
        }
    return {}


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
