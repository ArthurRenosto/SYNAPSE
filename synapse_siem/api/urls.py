"""
URL configuration for api project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/logs/', include('synapse_siem.app.logs.urls')),
]
