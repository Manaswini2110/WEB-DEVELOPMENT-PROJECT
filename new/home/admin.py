from django.contrib import admin
from .models import *

@admin.register(Product)
class CartRegister(admin.ModelAdmin):
    list_display = ['id','name','description','category','price','image']

@admin.register(Category)
class CategoryRegister(admin.ModelAdmin):
    list_display = ['id','category','gender']
    list_filter = ['gender']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'size', 'price', 'quantity', 'total_price')
    list_filter = ('name', 'size')

    def product(self, obj):
        return obj.product.name if obj.product else None
    product.short_description = 'Product'

@admin.register(Recommended)
class Recommended(admin.ModelAdmin):
    list_display = ['id','name','description','gender','price','image_1','image_2','image_3','image_4']

@admin.register(OrderDetail)
class OrderDetails(admin.ModelAdmin):
    list_display = ['id','first_name','last_name','email','phone','pincode','address','payment_status']

@admin.register(OrderDetailItem)
class OrderDetailItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'size' , 'quantity', 'total_price']

    def product(self, obj):
        if obj.product:
            return obj.product.name
        else:
            return '-'
    product.short_description = 'Product'
    
