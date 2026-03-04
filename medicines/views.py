from django.shortcuts import render, redirect, get_object_or_404
from .models import Company
from django import forms


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