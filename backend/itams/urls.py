from django.conf import settings  # type: ignore[import]
from django.conf.urls.static import static  # type: ignore[import]
from django.contrib import admin # type: ignore[import]
from django.urls import path, include  # type: ignore[import]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
