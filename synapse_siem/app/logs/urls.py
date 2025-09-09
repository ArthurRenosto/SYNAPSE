from django.urls import path
from .views import LogAnalysisView, LogUploadView, LogFileDeleteView, AnalysisHistoryView

urlpatterns = [
    path('', LogAnalysisView.as_view(), name='log-analysis'),
    path('upload/', LogUploadView.as_view(), name='log-upload'),
    path('files/<int:file_id>/', LogFileDeleteView.as_view(), name='log-file-delete'),
    path('history/', AnalysisHistoryView.as_view(), name='analysis-history'),
]
