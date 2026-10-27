from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Brand, Category, Model, PurchaseMode, Vendor, normalize_name


class IdentityConflict(Exception):
    def __init__(self, field, identity):
        self.identity = identity
        self.detail = {field: ['A catalog record with this identity already exists.']}
        super().__init__(self.detail)


class CatalogSerializer(serializers.ModelSerializer):
    """Validate the stored identity before any write, including partial updates."""
    def get_fields(self):
        fields = super().get_fields()
        name = fields[self.Meta.model.name_field]
        name.validators = [validator for validator in name.validators
                           if not isinstance(validator, UniqueValidator)]
        return fields

    def get_validators(self):
        # The normalized, Brand-scoped check below owns catalog uniqueness.
        return []

    def identity(self, attrs):
        model = self.Meta.model
        field = model.name_field
        name = attrs.get(field, getattr(self.instance, field, ''))
        brand = attrs.get('brand', getattr(self.instance, 'brand', None))
        return f'{brand.pk if brand else "unbranded"}: {name}' if model is Model else name

    def validate(self, attrs):
        model = self.Meta.model
        field = model.name_field
        if field in attrs:
            attrs[field] = normalize_name(attrs[field])
            if not attrs[field]:
                raise serializers.ValidationError({field: 'This field may not be blank.'})
        name = attrs.get(field, getattr(self.instance, field, ''))
        matches = model.objects.filter(**{f'{field}__iexact': name})
        if model is Model:
            matches = matches.filter(brand=attrs.get('brand', getattr(self.instance, 'brand', None)))
        if self.instance:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise IdentityConflict(field, self.identity(attrs))
        return attrs


class CategorySerializer(CatalogSerializer):
    class Meta:
        model = Category
        fields = ('id', 'category_name')


class BrandSerializer(CatalogSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'brand_name')


class ModelSerializer(CatalogSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), allow_null=False)

    class Meta:
        model = Model
        fields = ('id', 'model_name', 'brand')


class PurchaseModeSerializer(CatalogSerializer):
    class Meta:
        model = PurchaseMode
        fields = ('id', 'purchase_mode')


class VendorSerializer(CatalogSerializer):
    class Meta:
        model = Vendor
        fields = ('id', 'name', 'contact_person', 'phone', 'email')
