from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='get_range')
def get_range(number):
    """
    Возвращает диапазон чисел. Используется для отрисовки звезд рейтинга.
    Например, если рейтинг 4, вернет range(4), что позволит циклу
    в шаблоне выполниться 4 раза.
    """
    if number is None:
        return range(0)
    return range(int(number))
