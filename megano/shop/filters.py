import logging
import django_filters
from .models import Product
from django.db.models import Q


logger = logging.getLogger(__name__)


class ProductFilter(django_filters.FilterSet):

    price_range = django_filters.CharFilter(method='custom_filter')

    class Meta:
        model = Product
        fields = ['price_range']

    def custom_filter(self, queryset, name, value):
        if value:
            value_list = value.split(';')
            price_min = int(value_list[0])
            price_max = int(value_list[1])
            return queryset.filter(price__gte=price_min).filter(price__lte=price_max)
        else:
            return queryset

