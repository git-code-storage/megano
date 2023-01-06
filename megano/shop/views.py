from django.shortcuts import render, redirect
from django.db.models import Q
from django.views.generic import DetailView, ListView
from .utils import get_total_cart_items
from .models import *


def index(request):
    items = Product.objects.select_related('category').filter(is_active=True).order_by('-index', '-sold')
    q = Q(is_active=True) & Q(is_limited=True)
    is_limited = Product.objects.select_related('category').filter(q).order_by('-index', '-sold')
    products = items[:4]
    products_hide_md = items[5:7]
    products_hide_1450 = items[7:9]
    total_cart_items, total_cost = get_total_cart_items(request)
    context = {
        'products': products,
        'products_hide_md': products_hide_md,
        'products_hide_1450': products_hide_1450,
        'is_limited': is_limited,
        'total_cart_items': total_cart_items,
        'total_cost': total_cost,
    }
    return render(request, 'shop/index.html', context=context)


def add_cart(request, product_slug):
    if request.user.is_anonymous:
        if 'cart' in request.session:
            if product_slug not in request.session['cart'].keys():
                request.session['cart'][product_slug] = 1
                request.session.modified = True
            else:
                request.session['cart'][product_slug] += 1
                request.session.modified = True
        else:
            request.session['cart'] = {product_slug: 1, }
            request.session.modified = True
    else:
        product = Product.objects.get(slug=product_slug)
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        order.save()
        orderitem, created = OrderItem.objects.get_or_create(
            product=product,
            order=order,
        )
        orderitem.quantity += 1
        orderitem.save()
    return redirect(request.META.get('HTTP_REFERER'))


def cart(request):
    cart_items = order.orderitem_set.select_related('product').all()
    total_cart_items = get_total_cart_items(request)
    context = {'cart_items': cart_items, 'total_cart_items': total_cart_items}
    pass


class ProductByCategoryListView(ListView):

    template_name = 'shop/catalog.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        q = Q(is_active=True) & Q(category__slug=self.kwargs.get('category_slug'))
        return Product.objects.filter(q)


class ProductDetailView(DetailView):

    model = Product
    context_object_name = 'product'
    template_name = 'shop/product.html'
    slug_url_kwarg = 'product_slug'

