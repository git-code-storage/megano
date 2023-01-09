import logging
import django_filters
from .models import Product


logger = logging.getLogger(__name__)


class ProductFilter(django_filters.FilterSet):

    price_range = django_filters.CharFilter(method='price_filter')
    name = django_filters.CharFilter(lookup_expr='icontains')
    onhand = django_filters.CharFilter(method='onhand_filter')
    freedelivery = django_filters.CharFilter(method='freedelivery_filter')

    class Meta:
        model = Product
        fields = ['price_range']

    def price_filter(self, queryset, name, value):
        if value:
            value_list = value.split(';')
            price_min = int(value_list[0])
            price_max = int(value_list[1])
            return queryset.filter(price__gte=price_min).filter(price__lte=price_max)
        else:
            return queryset

    def onhand_filter(self, queryset, name, value):
        if value:
            if value == 'on':
                return queryset.filter(amount__gt=0)
        else:
            return queryset

    def freedelivery_filter(self, queryset, name, value):
        if value:
            if value == 'on':
                return queryset.filter(price__gte=300)
        else:
            return queryset

