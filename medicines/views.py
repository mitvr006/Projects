from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Sale
from django import forms
from django.utils import timezone
from django.db.models import Sum
from datetime import date, timedelta
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import json, csv
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def home(request):
    return render(request, 'home.html')

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_staff(user):
    return user.groups.filter(name='Staff').exists()


# ===== sale CRUD START =====
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['medicine', 'quantity']

def sale_create(request):
    form = SaleForm(request.POST or None)

    if form.is_valid():
        try:
            sale = form.save(commit=False)

            medicine = sale.medicine
            quantity = sale.quantity

            # stock check
            if quantity <= 0:
                messages.error(request, "Quantity must be greater than 0")
                return redirect('sale_create')

            if quantity > medicine.quantity:
                messages.error(request, "Not enough stock availablel")
                return redirect('sale_create')
        
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

            messages.success(request, "Sale completed successfully!")

            return redirect('sale_invoice', pk=sale.pk)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('sale_create')
        
    return render(request, 'sales/sale_form.html', {'form': form})

def sale_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/invoice.html', {'sale': sale})

@login_required
def sale_list(request):
    sales = Sale.objects.select_related('medicine').all()
    return render(request, 'sales/sale_list.html', {'sales': sales})


# ===== company CRUD START =====

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

@login_required
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'companies/company_list.html', {'companies': companies})


def company_create(request):
    form = CompanyForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Company added successfully!")
        return redirect('company_list')
    
    messages.error(request, "Something went wrong!")
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

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'gst': forms.NumberInput(attrs={'class': 'form-control'}),
        }


def medicine_list(request):

    query = request.GET.get('q')

    if query:
        medicines = Medicine.objects.filter(name__icontains=query)
    else:
        medicines = Medicine.objects.all()

    return render(request, 'medicines/medicine_list.html', {
        'medicines': medicines
    })


from django.contrib import messages

def medicine_create(request):
    form = MedicineForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            medicine = form.save(commit=False)

            # Custom validation
            if medicine.price <= 0:
                messages.error(request, "Price must be greater than 0")
                return render(request, 'medicines/medicine_form.html', {'form': form})
            
            if medicine.quantity < 0:
                messages.error(request, "Quantity cannot be negative")
                return render(request, 'medicines/medicine_form.html', {'form': form})
            
            medicine.save()
            messages.success(request, "Medicine added successfully!")
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

@login_required
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


def login_view(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
        
    return render(request, 'auth/login.html')    

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def is_staff(user):
    return user.groups.filter(name='Staff').exists()

@login_required
def export_sales_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Medicine', 'Quantity', 'Total Price', 'Date'])

    sales = Sale.objects.all()

    for sale in sales:
        writer.writerow([
            sale.medicine.name,
            sale.quantity,
            sale.total_price,
            sale.date
        ])

    return response   

def generate_invoice_pdf(request, pk):
    sale = Sale.objects.get(pk=pk)

    template = get_template('sales/invoice_pdf.html')
    html = template.render({'sale': sale})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response
    ) 

    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    
    return response

