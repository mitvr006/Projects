from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Sale
from django import forms

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
        
        # Total price calculate
        sale.total_price = medicine.price * quantity

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
    medicines = Medicine.objects.select_related('company').all()
    return render(request, 'medicines/medicine_list.html', {'medicines': medicines})


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

