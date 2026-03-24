from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
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
    path('sales/invoice/<int:pk>/', views.sale_invoice, name='sale_invoice'),
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/low_stock/', views.low_stock, name='low_stock'),
    path('reports/expiry_alert/', views.expiry_alert, name='expiry_alert'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('export-sales/', views.export_sales_csv, name='export_sales'),
    path('invoice/pdf/<int:pk>/', views.generate_invoice_pdf, name='invoice_pdf'),
]