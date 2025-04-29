import django_filters
from django import template, forms
from django.db.models import Q

from rental.models import Car, Dealer

register = template.Library()


@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


class CarCapacityFilter(django_filters.NumberFilter):
    """Чекбоксы по категориям вместимости."""

    def filter(self, qs, value):
        if value is None:
            return qs
        if value >= 8:
            return qs.filter(seats__gte=8)
        return qs.filter(seats=value)


class CarFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='filter_q',
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Марка или модель…'})
    )

    car_type = django_filters.MultipleChoiceFilter(
        choices=Car.CarType.choices,
        widget=forms.CheckboxSelectMultiple,
        label='Тип'
    )

    # Слайдер “минимум мест”
    seats = django_filters.NumberFilter(
        field_name='seats',
        lookup_expr='gte',
        label='Мин. мест',
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '2',
            'max': '10',
            'step': '1',
            'class': 'range range-primary w-full'
        })
    )
    price_to = django_filters.NumberFilter(
        field_name='price_per_day',
        lookup_expr='lte',
        label='Цена до (₸)'
    )

    transmission = django_filters.MultipleChoiceFilter(
        choices=Car.TransmissionTypes.choices,
        widget=forms.CheckboxSelectMultiple,
        label='Коробка'
    )

    dealer = django_filters.ModelMultipleChoiceFilter(
        queryset=Dealer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Дилер'
    )

    class Meta:
        model = Car
        fields = []

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(brand__icontains=value) | Q(model__icontains=value)
        )

    def filter_seats(self, queryset, name, value):
        # если пользователь указал 8, показываем 8+
        try:
            v = int(value)
        except (TypeError, ValueError):
            return queryset
        if v >= 8:
            return queryset.filter(seats__gte=8)
        return queryset.filter(seats=v)
