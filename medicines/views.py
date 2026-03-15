from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Sale
from django import forms
from django.utils import timezone
from django.db.models import Sum
from datetime import date, timedelta
import json

# ===== sale CRUD START =====
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['medicine', 'quantity']

def sale_create(request):
    form = SaleForm(request.POST or None)

    if form.is_valid():
        sale = form.save(commit=False)

        medicine = sale.medicine
        quantity = sale.quantity

        # stock check
        if quantity > medicine.quantity:
            return render(request, 'sales/sale_form.html',{
              'form': form,
              'error': "Not enough stock availablel"  
            })
        
        # base price
        base_price = medicine.price * quantity

        # GST calculation
        gst_amount = base_price * (medicine.gst / 100)

        total = base_price + gst_amount
        
        # Total price calculate
        sale.total_price = total

        # stock reduce
        medicine.quantity -= quantity
        medicine.save()

        sale.save()

        return redirect('sale_invoice', pk=sale.pk)

    return render(request, 'sales/sale_form.html', {'form': form})

def sale_invoice(request, pk):
    sale = Sale.objects.get(pk=pk)
    return render(request, 'sales/invoice.html', {'sale': sale})

def sale_list(request):
    sales = Sale.objects.select_related('medicine').all()
    return render(request, 'sales/sale_list.html', {'sales': sales})


# ===== company CRUD START =====

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


def company_list(request):
    companies = Company.objects.all()
    return render(request, 'companies/company_list.html', {'companies': companies})


def company_create(request):
    form = CompanyForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('company_list')
    return render(request, 'companies/company_form.html', {'form': form})


def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, instance=company)
    if form.is_valid():
        form.save()
        return redirect('company_list')
    return render(request, 'companies/company_form.html', {'form': form})


def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        company.delete()
        return redirect('company_list')
    return render(request, 'companies/company_delete.html', {'company': company})


# ===== MEDICINE CRUD START =====

from .models import Medicine


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = '__all__'


def medicine_list(request):

    query = request.GET.get('q')

    if query:
        medicines = Medicine.objects.filter(name__icontains=query)
    else:
        medicines = Medicine.objects.all()

    return render(request, 'medicines/medicine_list.html', {
        'medicines': medicines
    })


def medicine_create(request):
    form = MedicineForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('medicine_list')
    return render(request, 'medicines/medicine_form.html', {'form': form})


def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=medicine)
    if form.is_valid():
        form.save()
        return redirect('medicine_list')
    return render(request, 'medicines/medicine_form.html', {'form': form})


def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.delete()
        return redirect('medicine_list')
    return render(request, 'medicines/medicine_delete.html', {'medicine': medicine})


# ===== Daily Sales Report START =====

def daily_report(request):
    today = timezone.now().date()

    sales = Sale.objects.filter(date__date=today)

    total_sales =sales.count()

    total_revenue = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0

    return render(request, 'reports/daily_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'today': today
    })

def low_stock (request):
    medicines = Medicine.objects.filter(quantity__lt=5)

    return render(request, 'reports/low_stock.html',{
        'medicines': medicines
    })


def expiry_alert(request):
    today = date.today()
    alert_date = today + timedelta(days=30)

    medicines = Medicine.objects.filter(expiry_date__lte=alert_date)

    return render(request, 'reports/expiry_alert.html', {
        'medicines': medicines
    })


def dashboard(request):

    total_companies = Company.objects.count()
    total_medicines = Medicine.objects.count()
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    today = timezone.now().date()
    last_week = today - timedelta(days=7)

    sales = Sale.objects.filter(date__date__gte=last_week)

    sales_dates = []
    sales_amounts = []

    for sale in sales:
        sales_dates.append(sale.date.strftime("%Y-%m-%d"))
        sales_amounts.append(sale.total_price)

    context = {
        'total_companies': total_companies,
        'total_medicines': total_medicines,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'sales_dates': json.dumps(sales_dates),
        'sales_amounts': json.dumps(sales_amounts)
    }        

    return render(request, 'dashboard.html', context)