from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import *


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):

    list_display = ('name', )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = ('name', 'price', 'amount', 'category', 'is_limited', 'index', 'sold', 'is_active',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = ('user', 'product', 'feedback', 'score',)
    list_filter = ('user', 'product', 'score',)
    search_fields = ('user', 'product',)
    ordering = ('creation_date',)
    readonly_fields = ('user', 'product', 'feedback', 'score',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = ('id', 'order', 'payment_way', 'date_of_creation', 'date_of_update', 'complete', 'error_status',
                    'error_msg',)
    list_filter = ('payment_way', 'complete', 'error_status',)
    search_fields = ('order', )
    readonly_fields = ('date_of_creation', 'date_of_update',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = ('order', 'product', 'price', 'quantity', 'date_added',)
    search_fields = ('order', 'product', 'date_added',)
    readonly_fields = ('date_added',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_of_creation', 'date_of_changing', 'complete',)
    list_filter = ('complete',)
    search_fields = ('id', 'customer', 'date_of_creation',)
    readonly_fields = ('date_of_creation', 'date_of_changing',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'comment', 'type_of_delivery', 'complete',)
    list_filter = ('type_of_delivery', 'complete',)
    search_fields = ('order', 'address',)


@admin.register(TypeOfDelivery)
class TypeOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ('type_of_delivery', 'min_order', 'cost', 'additional_cost',)
