from rest_framework.routers import DefaultRouter

from .views import (AssignmentViewSet, AssetDocumentViewSet, AssetImageViewSet, AssetViewSet,
                    CheckoutViewSet, ProcurementViewSet, ServiceRecordViewSet,
                    TransferViewSet)

router = DefaultRouter()
router.register('asset', AssetViewSet, basename='asset')
router.register('asset_image', AssetImageViewSet, basename='asset-image')
router.register('asset_document', AssetDocumentViewSet, basename='asset-document')
router.register('procurement', ProcurementViewSet, basename='procurement')
router.register('checkout', CheckoutViewSet, basename='checkout')
router.register('assignment', AssignmentViewSet, basename='assignment')
router.register('transfer', TransferViewSet, basename='transfer')
router.register('service', ServiceRecordViewSet, basename='service')

urlpatterns = router.urls
