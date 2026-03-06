from django.urls import path
from . import views

urlpatterns = [
    path('companies/', views.company_list, name='company_list'),
    path('companies/add/', views.company_create, name='company_create'),
    path('companies/edit/<int:pk>/', views.company_update, name='company_update'),
    path('companies/delete/<int:pk>/', views.company_delete, name='company_delete'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.medicine_create, name='medicine_create'),
    path('medicines/edit/<int:pk>/', views.medicine_update, name='medicine_update'),
    path('medicines/delete/<int:pk>/', views.medicine_delete, name='medicine_delete'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/add/', views.sale_create, name='sale_create'),
]