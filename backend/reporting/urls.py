from django.urls import path

from .views import ReportExportView, ReportView, charts, dashboard

urlpatterns = [
    path('dashboard/', dashboard),
    path('charts/<str:name>/', charts),
    path('reports/', ReportView.as_view()),
    path('reports/<str:key>/', ReportView.as_view()),
    path('reports/<str:key>/export/<str:fmt>/', ReportExportView.as_view()),
]
