from .models import *


def get_order_items_annonimous(products, cart):
    cart_items_list = []
    for product in products:
        cart_items_list.append({'product': product, 'quantity': cart[product.slug]})
    return cart_items_list


def get_total_cart_items(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total_cart_items = order.get_cart_items
    else:
        total_cart_items = 0
        if request.session['cart']:
            products = request.session['cart'].keys()
            for product in products:
                total_cart_items += request.session['cart'][product]
    return total_cart_items


