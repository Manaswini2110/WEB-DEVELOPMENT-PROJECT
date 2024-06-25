from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('K','Kids')
    ]
    category = models.CharField(max_length=100, default=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.category

class Product(models.Model):
    name_validator = RegexValidator(
    regex=r'^[A-Za-z0-9?!,.\'\s-]+$',
    message="Product name can only contain letters, numbers, spaces, '?', '!', ',', '.', hyphens, and apostrophe characters."
    )

    name = models.CharField(
        max_length=255,
        validators=[name_validator],
        default=False,
    )
    description = models.TextField()
    image = models.ImageField(upload_to="Product", default="")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', default=None)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_product_price(self):
        return self.price
    
class Recommended(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('K','Kids')
    ]
    name_validator = RegexValidator(
    regex=r'^[A-Za-z0-9?!,.\'\s-]+$',
    message="Product name can only contain letters, numbers, spaces, '?','&', '!', '^','-','_','.', hyphens, and apostrophe characters."
    )

    name = models.CharField(
        max_length=255,
        validators=[name_validator],
    )
    description = models.TextField()
    image_1 = models.ImageField(upload_to="Recommended", default="")
    image_2 = models.ImageField(upload_to="Recommended", default="")
    image_3 = models.ImageField(upload_to="Recommended", default="")
    image_4 = models.ImageField(upload_to="Recommended", default="")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default=False)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_product_price(self):
        return self.price
    
class CartItem(models.Model):
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    product = models.CharField(max_length=255, null=True, blank=True,default=False)
    size = models.CharField(max_length = 10,default=False)
    price = models.IntegerField(default = False)
    quantity = models.IntegerField(default = 0)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    class Meta:
        unique_together = ('name', 'product', 'size')

    def __str__(self):
        if self.product:
            return f"{self.name} - {self.product} - {self.size}"
        else:
            return "Invalid Cart Item"

    
class OrderDetail(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20)

    def __str__(self):
        return f"Order by {self.first_name} {self.last_name}"

class OrderDetailItem(models.Model):
    order = models.ForeignKey(
        'OrderDetail',
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('Order')
    )
    product = models.CharField(max_length=255, verbose_name=_('Product'))
    size = models.CharField(max_length = 10,verbose_name = _('Size'))
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Price'))

    class Meta:
        verbose_name = _('Order Detail Item')
        verbose_name_plural = _('Order Detail Items')
        
