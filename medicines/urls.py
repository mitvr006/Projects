from django.urls import path
from . import views

urlpatterns = [
    path('companies/', views.company_list, name='company_list'),
    path('companies/add/', views.company_create, name='company_create'),
    path('companies/edit/<int:pk>/', views.company_update, name='company_update'),
    path('companies/delete/<int:pk>/', views.company_delete, name='company_delete'),
]