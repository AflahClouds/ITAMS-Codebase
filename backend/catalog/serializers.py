from rest_framework import serializers

from .models import Brand, Category, Model, PurchaseMode, Vendor


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'category_name')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'brand_name')


class ModelSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), allow_null=False)

    class Meta:
        model = Model
        fields = ('id', 'model_name', 'brand')


class PurchaseModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseMode
        fields = ('id', 'purchase_mode')


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('id', 'name', 'contact_person', 'phone', 'email')
