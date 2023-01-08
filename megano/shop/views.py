import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.db.models import Q
from django.views.generic import DetailView, ListView
from .utils import get_total_cart_items
from .models import Product, Order, OrderItem
from .forms import PriceForm
from .filters import ProductFilter

logger = logging.getLogger(__name__)


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


def products_by_category(request, category_slug, sort):

    if request.META.get('HTTP_REFERER'):
        refer_list = request.META.get('HTTP_REFERER').split('/')
        if len(refer_list) == 7:
            filters = refer_list[6]
    else:
        filters = ''
    if request.GET.get('sort_by'):
        sort = request.GET.get('sort_by')
        return redirect(f'../../{category_slug}/{sort}/{filters}')

    q = Q(is_active=True) & Q(category__slug=category_slug)
    if sort == 'cost_asc':
        ordering = 'price'
    elif sort == 'cost_desc':
        ordering = '-price'
    elif sort == 'pop_asc':
        ordering = 'sold'
    elif sort == 'pop_desc':
        ordering = '-sold'
    elif sort == 'new_asc':
        ordering = 'creation_date'
    elif sort == 'new_desc':
        ordering = '-creation_date'
    elif sort == 'feed_asc':
        ordering = 'index'
    elif sort == 'feed_desc':
        ordering = '-index'
    else:
        ordering = 'price'
    queryset = Product.objects.filter(q).order_by(ordering)

    product_filter = ProductFilter(request.GET, queryset=queryset)
    queryset = product_filter.qs
    paginator = Paginator(queryset, 8)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)


    context = {}
    total_cart_items, total_cost = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['sort'] = sort
    context['products'] = page.object_list
    context['page'] = page

    return render(request, 'shop/catalog.html', context)


class ProductByCategoryListView(ListView):

    template_name = 'shop/catalog.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        q = Q(is_active=True) & Q(category__slug=self.kwargs.get('category_slug'))
        self.queryset = Product.objects.filter(q)
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug')
        if request.META.get('HTTP_REFERER'):
            refer_list = request.META.get('HTTP_REFERER').split('/')
            if len(refer_list) == 7:
                filters = refer_list[6]
        else:
            filters = ''
        if self.request.GET.get('sort_by'):
            sort = self.request.GET.get('sort_by')
            return redirect(f'../../{category_slug}/{sort}/{filters}')
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['filter'] = ProductFilter(self.request.GET, queryset=self.get_queryset())
        total_cart_items, total_cost = get_total_cart_items(self.request)
        context['total_cart_items'] = total_cart_items
        context['total_cost'] = total_cost
        sort = self.request.META.get("PATH_INFO").split('/')[3]
        context['sort'] = sort
        # price = self.request.GET.get('price')
        # if price:
        #     price_list = price.split(';')
        #     price_from = int(price_list[0])
        #     price_to = int(price_list[1])
        # else:
        #     price_from = 0
        #     price_to = 100000
        title = self.request.GET.get('title')
        if not title:
            title = ''
        onhand = self.request.GET.get('onhand')
        freedelivery = self.request.GET.get('freedelivery')

        # context['price_from'] = price_from
        # context['price_to'] = price_to
        if title:
            context['title'] = title
        if onhand == 'on':
            context['onhand'] = 'checked'
        if freedelivery == 'on':
            context['freedelivery'] = 'checked'

        return context

    def get_ordering(self):
        sort = self.kwargs.get("sort")
        if sort == 'cost_asc':
            self.ordering = 'price'
        elif sort == 'cost_desc':
            self.ordering = '-price'
        elif sort == 'pop_asc':
            self.ordering = 'sold'
        elif sort == 'pop_desc':
            self.ordering = '-sold'
        elif sort == 'new_asc':
            self.ordering = 'creation_date'
        elif sort == 'new_desc':
            self.ordering = '-creation_date'
        elif sort == 'feed_asc':
            self.ordering = 'index'
        elif sort == 'feed_desc':
            self.ordering = '-index'
        return self.ordering


class ProductDetailView(DetailView):

    model = Product
    context_object_name = 'product'
    template_name = 'shop/product.html'
    slug_url_kwarg = 'product_slug'


def testform(request):
    form = PriceForm(request.GET)
    return render(request, 'shop/testform.html', {'form': form})

