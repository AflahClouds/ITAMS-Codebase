from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (AssetDocumentViewSet, AssetImageViewSet, AssetViewSet,
                    AuditLogViewSet, BrandViewSet, CategoryViewSet,
                    ChangePasswordView, CheckoutViewSet, DepartmentViewSet,
                    LocationViewSet, LoginView, LogoutView, MeView,
                    ModelViewSet, NotificationViewSet, PermissionViewSet,
                    ProcurementViewSet, PurchaseModeViewSet, ReportExportView,
                    ReportView, RoleViewSet, SettingViewSet, TransferViewSet,
                    UserViewSet, charts, dashboard)

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('brand', BrandViewSet, basename='brand')
router.register('model', ModelViewSet, basename='model')
router.register('purchase_mode', PurchaseModeViewSet, basename='purchase-mode')
router.register('department', DepartmentViewSet, basename='department')
router.register('location', LocationViewSet, basename='location')
router.register('role', RoleViewSet, basename='role')
router.register('permission', PermissionViewSet, basename='permission')
router.register('user', UserViewSet, basename='user')
router.register('asset', AssetViewSet, basename='asset')
router.register('asset_image', AssetImageViewSet, basename='asset-image')
router.register('asset_document', AssetDocumentViewSet, basename='asset-document')
router.register('procurement', ProcurementViewSet, basename='procurement')
router.register('checkout', CheckoutViewSet, basename='checkout')
router.register('transfer', TransferViewSet, basename='transfer')
router.register('notification', NotificationViewSet, basename='notification')
router.register('audit', AuditLogViewSet, basename='audit')
router.register('setting', SettingViewSet, basename='setting')

urlpatterns = [
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/me/', MeView.as_view()),
    path('auth/change-password/', ChangePasswordView.as_view()),
    path('dashboard/', dashboard),
    path('charts/<str:name>/', charts),
    path('reports/', ReportView.as_view()),
    path('reports/<str:key>/', ReportView.as_view()),
    path('reports/<str:key>/export/<str:fmt>/', ReportExportView.as_view()),
] + router.urls
