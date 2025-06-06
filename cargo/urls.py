from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('report/', views.report, name='report'),
    path('landing/', views.landing, name='landing'),
    path('register/', views.register_user, name='register'),
    path('agregar-conductor/', views.add_driver, name='add_driver'),
    ]
