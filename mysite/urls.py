from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('cargo.urls')),  # Include the URLs from the cargo app
]
