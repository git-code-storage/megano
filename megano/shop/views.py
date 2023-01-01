from django.shortcuts import render
from django.db.models import Q
from django.views.generic import DetailView, ListView
from .models import *


def index(request):
    items = Product.objects.select_related('category').filter(is_active=True).order_by('-index', '-sold')
    q = Q(is_active=True) & Q(is_limited=True)
    is_limited = Product.objects.select_related('category').filter(q).order_by('-index', '-sold')
    products = items[:4]
    products_hide_md = items[5:7]
    products_hide_1450 = items[7:9]
    context = {
        'products': products,
        'products_hide_md': products_hide_md,
        'products_hide_1450': products_hide_1450,
        'is_limited': is_limited,
    }
    return render(request, 'shop/index.html', context=context)


class ProductByCategoryListView(ListView):

    template_name = 'shop/catalog.html'

    def get_queryset(self):
        q = Q(is_active=True) & Q(category__slug=self.kwargs.get('category_slug'))
        return Product.objects.filter(q)
