from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cargo.urls')),  # Include the URLs from the cargo app
]
