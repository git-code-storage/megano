import logging
from shop.models import Product, Order, OrderItem
from .models import CustomUser
from datetime import datetime

logger = logging.getLogger(__name__)


def add_cart_to_user(request, form, view):
    if view == 'registration':
        email = form.cleaned_data.get('email')
    else:
        email = form.cleaned_data.get('username')
    logger.info(f'[{view}] - {datetime.now()} - Entered email: {email}')
    customer = CustomUser.objects.get(email=email)
    logger.info(f'[{view}] - {datetime.now()} - User: {customer.email}')
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    logger.info(f'[{view}] - {datetime.now()} - Order: {order.id}')
    order.save()
    if 'cart' in request.session:
        for item in request.session['cart'].keys():
            product = Product.objects.get(slug=item)
            logger.info(f'[{view}] - {datetime.now()} - Product: {product.name}')
            orderitem, created = OrderItem.objects.get_or_create(product=product, order=order)
            logger.info(f'[{view}] - {datetime.now()} - Orderitem: {orderitem.id}, '
                        f'quantity: {orderitem.quantity}')
            orderitem.quantity += request.session['cart'][item]
            logger.info(f'[{view}] - {datetime.now()} - Quantity after summ: {orderitem.quantity}')
            orderitem.save()
