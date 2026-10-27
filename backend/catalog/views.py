"""Catalog master data (B6). Reads need `asset_view`; the Employee Role gets no
B6 surface at all, so these viewsets deny own-records scope outright."""
from rest_framework import viewsets
from rest_framework.response import Response
from django.db import IntegrityError, transaction

from core.audit_mixins import AuditedMutationMixin
from core.mixins import MASTER_WRITE, ProtectedMasterDeleteMixin
from core.permissions import HasRolePermission, NotOwnRecordsScope
from core.services import log_action

from .models import Brand, Category, Model, PurchaseMode, Vendor
from .serializers import (BrandSerializer, CategorySerializer, IdentityConflict,
                          ModelSerializer, PurchaseModeSerializer,
                          VendorSerializer)


class CatalogIdentityMixin:
    """Keep rejected-write auditing outside the rolled-back savepoint.

    Returning the known conflict here avoids DRF's exception handler marking the
    entire ATOMIC_REQUESTS transaction for rollback, which would discard its audit.
    Unrelated validation and persistence errors retain their normal failure path.
    """
    def _write(self, operation, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return operation(request, *args, **kwargs)
        except IdentityConflict as exc:
            action = 'Create' if self.action == 'create' else 'Update'
            log_action(request, f'{action} Rejected', self.audit_module,
                       new_value=f'Identity conflict: {exc.identity}')
            return Response(exc.detail, status=400)

    def create(self, request, *args, **kwargs):
        return self._write(super().create, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self._write(super().update, request, *args, **kwargs)

    def _save(self, operation, serializer):
        model = serializer.Meta.model
        field = model.name_field
        constraint = {Category: 'uniq_category_name_ci', Brand: 'uniq_brand_name_ci',
                      Model: 'uniq_model_per_brand_ci', PurchaseMode: 'uniq_purchase_mode_ci',
                      Vendor: 'uniq_vendor_name_ci'}[model]
        identity = serializer.identity(serializer.validated_data)
        try:
            operation(serializer)
        except IntegrityError as exc:
            # Only our named identity constraint (or SQLite's exact unique-column
            # message) establishes a duplicate. Do not hide other storage failures.
            message = str(exc)
            named = getattr(getattr(exc.__cause__, 'diag', None), 'constraint_name', None)
            sqlite_column = f'UNIQUE constraint failed: {model._meta.db_table}.{field}'
            if named == constraint or message == f"UNIQUE constraint failed: index '{constraint}'" or (
                    model is not Model and message == sqlite_column):
                raise IdentityConflict(field, identity) from exc
            raise

    def perform_create(self, serializer):
        self._save(super().perform_create, serializer)

    def perform_update(self, serializer):
        self._save(super().perform_update, serializer)


class CategoryViewSet(CatalogIdentityMixin, AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Category"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Category.objects.all().order_by('category_name')
    serializer_class = CategorySerializer


class BrandViewSet(CatalogIdentityMixin, AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Brand"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Brand.objects.all().order_by('brand_name')
    serializer_class = BrandSerializer


class ModelViewSet(CatalogIdentityMixin, AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Model"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Model.objects.all().order_by('model_name')
    serializer_class = ModelSerializer


class PurchaseModeViewSet(CatalogIdentityMixin, AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Purchase Mode"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = PurchaseMode.objects.all().order_by('purchase_mode')
    serializer_class = PurchaseModeSerializer


class VendorViewSet(CatalogIdentityMixin, AuditedMutationMixin, ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    audit_module = "Vendor"
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = MASTER_WRITE
    queryset = Vendor.objects.all().order_by('name')
    serializer_class = VendorSerializer
