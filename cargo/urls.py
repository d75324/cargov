from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout_user, name='logout'),
    path('report/', views.report, name='report'),
    path('landing/', views.landing, name='landing'),
    path('register/', views.register_user, name='register'),
    path('agregar-conductor/', views.add_driver, name='add_driver'),
    path('agregar-vehiculo/', views.add_truck, name='add_truck'),
    #path('register-trip/<int:truck_id>/', views.register_trip, name='register_trip'),
    path('register-trip/', views.register_trip, name='register_trip'),
    path('travel/<int:trip_id>/', views.travel_actions, name='travel_actions'),
    path('ajax/get-truck-mileage/', views.get_truck_mileage, name='get_truck_mileage'),
    #path('travel-actions/<int:trip_id>/', views.travel_actions, name='travel_actions'),
    path('fuel-register/<int:trip_id>/', views.fuel_register, name='fuel_register'),
    path('unload-register/<int:trip_id>/', views.unload_register, name='unload_register'),
    path('travel-summary/<int:trip_id>/', views.travel_summary, name='travel_summary'),
    ]

