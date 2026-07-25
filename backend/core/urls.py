from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, NotificationViewSet, SettingViewSet

router = DefaultRouter()
router.register('notification', NotificationViewSet, basename='notification')
router.register('audit', AuditLogViewSet, basename='audit')
router.register('setting', SettingViewSet, basename='setting')

urlpatterns = router.urls
