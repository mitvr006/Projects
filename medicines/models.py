from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    expiry_date = models.DateField()

    def __str__(self):
        return self.name