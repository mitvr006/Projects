from django.contrib import admin
from .models import Company, Medicine, Sale
from datetime import date, timedelta

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')
    search_fields = ('name',)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'price', 'quantity', 'expiry_date')
    list_filter = ('company', 'expiry_date')
    search_fields = ('name',)

    def expiry_status(self, obj):
        if obj.expiry_date <= date.today() + timedelta(days=30):
            return "⚠ Expiring Soon"
        return "ok"
    
    expiry_status.short_description = "status"


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'quantity', 'total_price', 'date')
    list_filter = ('date',)


admin.site.site_header = "Medical Management Admin"
admin.site.site_title = "Medical System"
admin.site.index_title = "Welcome to Medical Dashboard"

