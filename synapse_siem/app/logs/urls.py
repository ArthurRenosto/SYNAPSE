from django.urls import path
from .views import LogAnalysisView, LogUploadView, LogFileDeleteView, AnalysisHistoryView, GeminiAnalyzeView

urlpatterns = [
    path('', LogAnalysisView.as_view(), name='log-analysis'),
    path('upload/', LogUploadView.as_view(), name='log-upload'),
    path('files/<int:file_id>/', LogFileDeleteView.as_view(), name='log-file-delete'),
    path('history/', AnalysisHistoryView.as_view(), name='analysis-history'),
    path('gemini/analyze/', GeminiAnalyzeView.as_view(), name='gemini-analyze'),
]
