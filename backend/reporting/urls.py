from django.urls import path

from .views import ChartView, DashboardView, ReportExportView, ReportView

urlpatterns = [
    path('dashboard/', DashboardView.as_view()),
    path('charts/<str:name>/', ChartView.as_view()),
    path('reports/', ReportView.as_view()),
    path('reports/<str:key>/', ReportView.as_view()),
    path('reports/<str:key>/export/<str:fmt>/', ReportExportView.as_view()),
]
