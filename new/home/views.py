from django.shortcuts import render,redirect
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.shortcuts import render
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.contrib import messages
import razorpay
from new import settings


class IndexView(APIView):
    def get(self, request):
        mens_categories = Category.objects.filter(gender='M')
        womens_categories = Category.objects.filter(gender='W')
        kids_categories = Category.objects.filter(gender='K')

        cart_item = CartItem.objects.all()

        cart_item_count = CartItem.objects.count()

        cart_total_price = CartItem.objects.aggregate(total_price=Sum('total_price'))['total_price']

        context = {
            'mens_categories': mens_categories,
            'womens_categories': womens_categories,
            'kids_categories': kids_categories,
            'cart_item_count': cart_item_count,
            'cart_total_price': cart_total_price,
            'cart_item': cart_item,
        }
        return render(request, 'index.html', context)
    
class ProductView(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Product Added Successfully'}, status=status.HTTP_201_CREATED)
        else:
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        category_men_id = request.GET.get('category_men')
        category_women_id = request.GET.get('category_women')
        category_kids_id = request.GET.get('category_kids')

        if category_men_id:
            products = Product.objects.filter(category_id=category_men_id)
        elif category_women_id:
            products = Product.objects.filter(category_id=category_women_id)
        elif category_kids_id:
            products = Product.objects.filter(category_id=category_kids_id)
        else:
            products = Product.objects.all()

        mens_categories = Category.objects.filter(gender='M')
        womens_categories = Category.objects.filter(gender='W')
        kids_categories = Category.objects.filter(gender='K')

        serializer = ProductSerializer(products, many=True)

        cart_item = CartItem.objects.all()

        cart_item_count = CartItem.objects.count()
        
        cart_total_price = CartItem.objects.aggregate(total_price=Sum('total_price'))['total_price']

        return render(request, 'product.html', {'products': serializer.data,'mens_categories': mens_categories,
            '   ': womens_categories,
            'kids_categories': kids_categories,'cart_item_count': cart_item_count,'cart_total_price': cart_total_price,'cart_item':cart_item})
    
    def put(self, request,  ):
        try:
            cart = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'message':'Cart not found'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,id):
        try:
            cart = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'message':'Cart not found'},status=status.HTTP_404_NOT_FOUND)
        
        cart.delete()
        return Response({'message':'Cart deleted successfully'},status=status.HTTP_200_OK)
    
class CategoryView(APIView):
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Category Added Successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_200_OK)
    
class ProductDetailView(APIView):
    def get(self, request, id):
        product = Product.objects.get(id=id)

        mens_categories = Category.objects.filter(gender='M')
        womens_categories = Category.objects.filter(gender='W')
        kids_categories = Category.objects.filter(gender='K')

        serializer = ProductSerializer(product)

        product = get_object_or_404(Product, pk=id)

        cart_item = CartItem.objects.all()
        
        cart_item_count = CartItem.objects.count()
        
        cart_total_price = CartItem.objects.aggregate(total_price=Sum('total_price'))['total_price']

        product_gender = product.category.gender
        
        recommended = Recommended.objects.filter(gender = product_gender)

        return render(request, 'details.html', {'product': serializer.data,'mens_categories': mens_categories,
            'womens_categories': womens_categories,
            'kids_categories': kids_categories,'cart_item_count': cart_item_count,'cart_total_price': cart_total_price,'cart_item':cart_item,
            'recommended':recommended})
            
class AddToCart(APIView):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size')

        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return redirect('error_page')
            
            total_price = product.price * quantity

            existing_cart_item = CartItem.objects.filter(name=request.user,product=product, size=size).first()
            if existing_cart_item:
                existing_cart_item.quantity += quantity
                existing_cart_item.total_price += total_price
                existing_cart_item.save()
            else:
                CartItem.objects.create(
                    name=request.user,
                    product=product,
                    size=size,
                    price=product.price,
                    quantity=quantity,
                    total_price=total_price,
                )

            messages.success(request, f'“{product.name}” has been added to your cart.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
class RecommendedCart(APIView):
    def post(self, request):
        recommended_id = request.POST.get('recommended_id')
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size')

        if recommended_id:
            try:
                recommended = Recommended.objects.get(pk=recommended_id)
            except Recommended.DoesNotExist:
                return redirect('error_page')
            
            total_price = recommended.price * quantity

            existing_cart_item = CartItem.objects.filter(name=request.user, product=recommended, size=size).first()
            if existing_cart_item:
                existing_cart_item.quantity += quantity
                existing_cart_item.total_price += total_price
                existing_cart_item.save()
            else:
                CartItem.objects.create(
                    name=request.user,
                    product=recommended,
                    size=size,
                    price=recommended.price,
                    quantity=quantity,
                    total_price=total_price
                )

            messages.success(request, f'“{recommended.name}” has been added to your cart.')
        
        return redirect(request.META.get('HTTP_REFERER', '/'))

class RemoveItem(APIView):
    def get(self, request, id):
        try:
            cart_item = CartItem.objects.get(id=id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
class ViewCart(APIView):
    def get(self,request):
        cart_item = CartItem.objects.all()
        cart_total = cart_item.aggregate(total=Sum('total_price'))['total']

        mens_categories = Category.objects.filter(gender='M')
        womens_categories = Category.objects.filter(gender='W')
        kids_categories = Category.objects.filter(gender='K')

        cart_item_count = CartItem.objects.count()
        
        cart_total_price = CartItem.objects.aggregate(total_price=Sum('total_price'))['total_price']

        context = {'cart_item':cart_item,'cart_total':cart_total,'mens_categories': mens_categories,
            'womens_categories': womens_categories,
            'kids_categories': kids_categories,'cart_item_count':cart_item_count,'cart_total_price': cart_total_price,}
        
        return render(request,'viewcart.html',context)
    
class RecommendedView(APIView):
    def post(self,request):
        serializer = RecommendedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Product added successfully'},status=status.HTTP_201_CREATED)
        else:
            print('Serializer error',serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SelectProductView(APIView):
    def get(self,request,id):
        recommended = Recommended.objects.get(id=id)
        context = {'recommended':recommended}
        return render(request,'recommended.html',context)
    
class CheckoutView(APIView):
    def get(self,request):
        cart_items = CartItem.objects.all()
        subtotal = cart_items.aggregate(subtotal=Sum('total_price'))['subtotal'] or 0

        mens_categories = Category.objects.filter(gender='M')
        womens_categories = Category.objects.filter(gender='W')
        kids_categories = Category.objects.filter(gender='K')

        cart_item_count = CartItem.objects.count()
        
        cart_total_price = CartItem.objects.aggregate(total_price=Sum('total_price'))['total_price']

        context = {
            'cart_items': cart_items,
            'cart_total_price':cart_total_price,
            'cart_item_count':cart_item_count,
            'subtotal': subtotal,
            'total': subtotal,
            'mens_categories': mens_categories,
            'womens_categories': womens_categories,
            'kids_categories': kids_categories,
            'cart_item_count': cart_item_count
        }
        return render(request, 'checkout.html', context)
    
class PlaceOrder(APIView):
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subtotal = request.POST.get('subtotal')
        total = request.POST.get('total')

        if not (first_name or last_name or address or pincode or phone or email):
            messages.error(request, 'Please fill in all the * details')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            order_detail = OrderDetail.objects.create(
                first_name=first_name,
                last_name=last_name,
                address=address,
                pincode=pincode,
                phone=phone,
                email=email,
                subtotal=subtotal,
                total=total
            )

            index = 1
            while True:
                product = request.POST.get(f'product_{index}')
                if not product:
                    break
                size = request.POST.get(f'size_{index}')
                quantity = int(request.POST.get(f'quantity_{index}'))
                total_price = float(request.POST.get(f'total_price_{index}'))
                
                OrderDetailItem.objects.create( 
                    order=order_detail,
                    product=product,
                    size=size,
                    quantity=quantity,
                    total_price=total_price
                )
                
                index += 1
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                razorpay_order = client.order.create({
                    'amount': int(total) * 100,  
                    'currency': 'INR',
                    'receipt': str(order_detail.id), 
                })

                order_detail.payment_status = 'Completed'
                order_detail.save()
        messages.success(request,'Your Order will be delivered in 3-4 working days')
        return redirect('order')
    
class OrderConfirmation(APIView):
    def get(self, request):
        orders = OrderDetailItem.objects.all()

        payment_status = OrderDetail.objects.values_list('payment_status', flat=True).first()

        subtotal = orders.aggregate(total_subtotal=Sum('total_price'))['total_subtotal']
        total_price = orders.aggregate(total_price=Sum('total_price'))['total_price']

        mens_categories = Category.objects.filter(gender='M')
        womens_categories = Category.objects.filter(gender='W')
        kids_categories = Category.objects.filter(gender='K')

        cart_item_count = CartItem.objects.count()
        
        cart_total_price = CartItem.objects.aggregate(total_price=Sum('total_price'))['total_price']

        context = {
            'orders': orders,
            'subtotal': subtotal,
            'cart_total_price':cart_total_price,
            'total_price': total_price,
            'mens_categories': mens_categories,
            'womens_categories': womens_categories,
            'kids_categories': kids_categories,
            'cart_item_count': cart_item_count,
            'payment_status': payment_status,
        }

        return render(request, 'order.html', context)