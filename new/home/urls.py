from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('product/', ProductView.as_view(), name='product'),
    path('category/', CategoryView.as_view(), name='category'),
    path('product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('add_to_cart', AddToCart.as_view(), name='add_to_cart'),
    path('remove/<id>', RemoveItem.as_view(), name='remove'),
    path('view/', ViewCart.as_view(), name='view'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('recommended/', RecommendedView.as_view(), name='recommended'),
    path('recommended/<int:id>', SelectProductView.as_view(), name='recommended_product'),
    path('recommended_cart',RecommendedCart.as_view(),name='recommended_cart'),
    path('place_order/', PlaceOrder.as_view(), name='place_order'),
    path('order/', OrderConfirmation.as_view(), name='order'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()
