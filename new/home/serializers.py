import base64
import os
from rest_framework import serializers
from .models import *
from rest_framework.response import Response
from rest_framework import status

class EncodedImageField(serializers.Field):
    def to_internal_value(self, data):
        if data is None:
            return None
        if ';base64,' not in data:
            raise serializers.ValidationError("Invalid image format")
        split_base_url_data = data.split(';base64,')
        img = base64.b64decode(split_base_url_data[1])
        return img

class CategoryNameField(serializers.CharField):
    def to_internal_value(self, data):
        try:
            # Try to find the category by name
            category = Category.objects.get(category=data)
            return category
        except Category.DoesNotExist:
            # Raise a validation error if the category does not exist
            raise serializers.ValidationError("Category with this name does not exist.")

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(write_only=True)
    category = CategoryNameField()

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        image_data = validated_data.pop('image', None)
        name = validated_data.get('name')
        category = validated_data.get('category')

        if Product.objects.filter(name=name, category=category).exists():
            raise serializers.ValidationError({'error': 'Product with the same name already exists'})

        converted_image = None
        if image_data:
            converted_image = self.convertBase64(image_data, name, category)

        product = Product.objects.create(image=converted_image, **validated_data)
        return product

    def convertBase64(self, image_data, name, category):
        if image_data is None:
            return None

        try:
            img_data = base64.b64decode(image_data)
            category_path = os.path.join("media", category.category)
            os.makedirs(category_path, exist_ok=True)
            filename = os.path.join(category_path, "images", f"{name}.png")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(img_data)
            # Return the path to the saved image
            return os.path.join(category.category, 'images', f"{name}.png")
        except Exception as e:
            raise serializers.ValidationError({'error': f'Error decoding image: {str(e)}'})
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url if instance.image else None
        return representation

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        category_name = validated_data.get('category')
        gender = validated_data.get('gender')
        
        if Category.objects.filter(category=category_name,gender=gender).exists():
            raise serializers.ValidationError("Category with the same name already exists.")
        
        return super().create(validated_data)
    
class RecommendedSerializer(serializers.ModelSerializer):
    image_1 = serializers.CharField(write_only=True)
    image_2 = serializers.CharField(write_only=True)
    image_3 = serializers.CharField(write_only=True)
    image_4 = serializers.CharField(write_only=True)

    class Meta:
        model = Recommended
        fields = '__all__'

    def create(self, validated_data):
        image_data_1 = validated_data.pop('image_1', None)
        image_data_2 = validated_data.pop('image_2', None)
        image_data_3 = validated_data.pop('image_3', None)
        image_data_4 = validated_data.pop('image_4', None)

        if not all([image_data_1, image_data_2, image_data_3, image_data_4]):
            raise serializers.ValidationError({'error': 'Please provide all four images'})

        name = validated_data.get('name')
        gender = validated_data.get('gender')

        if Recommended.objects.filter(name=name, gender=gender).exists():
            raise serializers.ValidationError({'error': 'Product with the same name already exists'})

        converted_images = []
        for image_data, gender in [
            (image_data_1, 'image_1'),
            (image_data_2, 'image_2'),
            (image_data_3, 'image_3'),
            (image_data_4, 'image_4'),
        ]:
            converted_image = self.convertBase64(image_data, name, gender)
            converted_images.append(converted_image)

        recommend = Recommended.objects.create(
            image_1=converted_images[0],
            image_2=converted_images[1],
            image_3=converted_images[2],
            image_4=converted_images[3],
            **validated_data
        )
        return recommend

    def convertBase64(self, image_data, name, gender):
        if image_data is None:
            return None

        try:
            img_data = base64.b64decode(image_data)
            category_path = os.path.join("media", gender)
            os.makedirs(category_path, exist_ok=True)
            filename = os.path.join(category_path, f"{name}.png")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(img_data)   
            return os.path.join(gender, f"{name}.png")
        except Exception as e:
            raise serializers.ValidationError({'error': f'Error decoding image: {str(e)}'})