from rest_framework import viewsets

from core.mixins import MASTER_WRITE, ProtectedMasterDeleteMixin
from core.permissions import HasRolePermission

from .models import Brand, Category, Model, PurchaseMode
from .serializers import (BrandSerializer, CategorySerializer,
                          ModelSerializer, PurchaseModeSerializer)


class CategoryViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Category.objects.all().order_by('category_name')
    serializer_class = CategorySerializer


class BrandViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Brand.objects.all().order_by('brand_name')
    serializer_class = BrandSerializer


class ModelViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Model.objects.all().order_by('model_name')
    serializer_class = ModelSerializer


class PurchaseModeViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = PurchaseMode.objects.all().order_by('purchase_mode')
    serializer_class = PurchaseModeSerializer
