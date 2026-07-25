from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (ChangePasswordView, DepartmentViewSet, LocationViewSet,
                    LoginView, LogoutView, MeView, PermissionViewSet,
                    RoleViewSet, UserViewSet)

router = DefaultRouter()
router.register('department', DepartmentViewSet, basename='department')
router.register('location', LocationViewSet, basename='location')
router.register('role', RoleViewSet, basename='role')
router.register('permission', PermissionViewSet, basename='permission')
router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/me/', MeView.as_view()),
    path('auth/change-password/', ChangePasswordView.as_view()),
] + router.urls
