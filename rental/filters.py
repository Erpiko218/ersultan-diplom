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
        widget=forms.TextInput(attrs={
            'placeholder': 'Марка или модель…',
            'class'      : 'input input-bordered w-full text-orange-500',
        })
    )

    # ПАРАМЕТР car_type ↔ HTML-name "car_type"
    car_type = django_filters.MultipleChoiceFilter(
        field_name='car_type',
        choices=Car.CarType.choices,
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "checkbox checkbox-sm checkbox-warning"   # DaisyUI «orange»
        }),
        label='Тип'
    )

    seats = django_filters.NumberFilter(
        field_name='seats', lookup_expr='gte', label='Мин. мест',
        widget=forms.NumberInput(attrs={
            'type' : 'range',
            'min'  : '2',
            'max'  : '10',
            'step' : '1',
            'class': 'range range-warning w-full'   # оранжевый бегунок DaisyUI
        })
    )

    # ────────── Слайдер «Цена до» ──────────
    price_to = django_filters.NumberFilter(
        field_name='price_per_day', lookup_expr='lte', label='Цена до (₸)',
        widget=forms.NumberInput(attrs={
            'type' : 'range',
            'min'  : '0',
            'max'  : '10000000',                    # ← новое значение
            'step' : '1000',
            'class': 'range range-warning w-full'
        })
    )

    transmission = django_filters.MultipleChoiceFilter(
        choices=Car.TransmissionTypes.choices,
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "checkbox checkbox-sm checkbox-warning"
        }),
        label='Коробка'
    )

    dealer = django_filters.ModelMultipleChoiceFilter(
        queryset=Dealer.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "checkbox checkbox-sm checkbox-warning"
        }),
        label='Дилер'
    )

    class Meta:
        model   = Car
        fields  = []

    # --- методы фильтрации ---
    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(brand__icontains=value) | Q(model__icontains=value))

    def filter_seats(self, queryset, name, value):
        try:
            v = int(value)
        except (TypeError, ValueError):
            return queryset
        return queryset.filter(seats__gte=8) if v >= 8 else queryset.filter(seats=v)