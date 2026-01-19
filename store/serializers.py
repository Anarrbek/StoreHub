from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'name_ru', 'name_kg', 'name_en', 'description', 'description_ru', 'description_kg', 'description_en', 'price', 'stock', 'category']
        read_only_fields = ['id']




