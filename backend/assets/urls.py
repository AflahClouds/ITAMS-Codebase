from rest_framework.routers import DefaultRouter

from .views import (AssetDocumentViewSet, AssetImageViewSet, AssetViewSet,
                    CheckoutViewSet, ProcurementViewSet, TransferViewSet)

router = DefaultRouter()
router.register('asset', AssetViewSet, basename='asset')
router.register('asset_image', AssetImageViewSet, basename='asset-image')
router.register('asset_document', AssetDocumentViewSet, basename='asset-document')
router.register('procurement', ProcurementViewSet, basename='procurement')
router.register('checkout', CheckoutViewSet, basename='checkout')
router.register('transfer', TransferViewSet, basename='transfer')

urlpatterns = router.urls
