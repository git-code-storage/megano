from django.db import models
from user.models import CustomUser, DeliveryAddress
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='icon_category/', null=True, blank=True)
    image = models.ImageField(upload_to='image_category/', null=True, blank=True)
    is_favourites = models.BooleanField(default=False)
    parent = TreeForeignKey(
        'self',
        related_name='children',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    # @property
    # def get_absolute_url(self):
    #     return reverse('product_by_category', kwargs={'category_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @property
    def image_url(self):
        try:
            url = self.icon.url
        except:
            url = ''
        return url

    class MPTTMeta:
        db_table = 'category'
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        order_insertion_by = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = RichTextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.PositiveSmallIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='goods/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_limited = models.BooleanField(default=False)
    index = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    sold = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'product'
        verbose_name = 'product'
        verbose_name_plural = 'products'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @property
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    feedback = models.TextField()
    score = models.PositiveSmallIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'feedback'
        verbose_name = 'feedback'
        verbose_name_plural = 'feedbacks'

    def __str__(self):
        return self.feedback


class Payment(models.Model):

    class PaymentWay(models.TextChoices):
        CARD = 'CARD', 'payment by card online'
        ACCOUNT = 'ACNT', "online from a random someone else's account"

    payment_way = models.CharField(
        max_length=4,
        choices=PaymentWay.choices,
        default=PaymentWay.CARD,
    )
    complete = models.BooleanField(default=False)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    date_of_update = models.DateTimeField(auto_now=True)
    error_msg = models.CharField(max_length=100, null=True, blank=True)
    error_status = models.BooleanField(default=False)
    order = models.ForeignKey('Order', on_delete=models.RESTRICT, blank=True, null=True)

    class Meta:
        db_table = 'payment'
        verbose_name = 'payment'
        verbose_name_plural = 'payments'

    def __str__(self):
        payment = f'Payment: order: {self.order.id}, total: {self.order.get_cart_total}, complete: {self.complete}'
        return payment


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, blank=True, null=True, related_name='orderproduct')
    order = models.ForeignKey('Order', on_delete=models.RESTRICT, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    @property
    def get_total(self):
        total = self.price * self.quantity
        return total

    class Meta:
        db_table = 'orderitem'
        verbose_name = 'orderitem'
        verbose_name_plural = 'orderitems'

    def __str__(self):
        return self.product


class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.RESTRICT, null=True, blank=True)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    date_of_changing = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'order'
        verbose_name = 'order'
        verbose_name_plural = 'orders'


class Delivery(models.Model):
    address = models.ForeignKey(DeliveryAddress, on_delete=models.RESTRICT, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, blank=True, null=True)
    comment = models.TextField()
    complete = models.BooleanField(default=False)
    type_of_delivery = models.ForeignKey('TypeOfDelivery', on_delete=models.RESTRICT, blank=True, null=True)

    def __str__(self):
        return self.address

    class Meta:
        db_table = 'delivery'
        verbose_name = 'delivery'
        verbose_name_plural = 'deliveries'


class TypeOfDelivery(models.Model):
    class Type(models.TextChoices):
        NORMAL = 'NORMAL', 'normal delivery method'
        EXPRESS = 'EXPRESS', 'express delivery method'

    type_of_delivery = models.CharField(
        max_length=7,
        choices=Type.choices,
        default=Type.NORMAL,
        unique=True
    )
    min_order = models.DecimalField(max_digits=8, decimal_places=2)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    additional_cost = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.type_of_delivery

    class Meta:
        db_table = 'type_of_delivery'
        verbose_name = 'type of delivery'
        verbose_name_plural = 'type of deliveries'
