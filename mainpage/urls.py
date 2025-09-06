from django.urls import path
from mainpage.views import index

urlpatterns = [
    path('', index)
]