from rest_framework.routers import DefaultRouter

from .views import (BrandViewSet, CategoryViewSet, ModelViewSet,
                    PurchaseModeViewSet, VendorViewSet)

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('brand', BrandViewSet, basename='brand')
router.register('model', ModelViewSet, basename='model')
router.register('purchase_mode', PurchaseModeViewSet, basename='purchase-mode')
router.register('vendor', VendorViewSet, basename='vendor')

urlpatterns = router.urls
