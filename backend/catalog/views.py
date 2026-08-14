"""Catalog master data (B6). Reads need `asset_view`; the Employee Role gets no
B6 surface at all, so these viewsets deny own-records scope outright."""
from rest_framework import viewsets

from core.audit_mixins import AuditedMutationMixin
from core.mixins import MASTER_WRITE, ProtectedMasterDeleteMixin
from core.permissions import HasRolePermission, NotOwnRecordsScope

from .models import Brand, Category, Model, PurchaseMode, Vendor
from .serializers import (BrandSerializer, CategorySerializer,
                          ModelSerializer, PurchaseModeSerializer,
                          VendorSerializer)


class CategoryViewSet(AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Category"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Category.objects.all().order_by('category_name')
    serializer_class = CategorySerializer


class BrandViewSet(AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Brand"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Brand.objects.all().order_by('brand_name')
    serializer_class = BrandSerializer


class ModelViewSet(AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Model"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Model.objects.all().order_by('model_name')
    serializer_class = ModelSerializer


class PurchaseModeViewSet(AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Purchase Mode"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = PurchaseMode.objects.all().order_by('purchase_mode')
    serializer_class = PurchaseModeSerializer


class VendorViewSet(AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Vendor"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Vendor.objects.all().order_by('name')
    serializer_class = VendorSerializer
