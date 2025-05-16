from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    original_password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class ProductGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.TextField()
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    SUPPLY_TYPE_CHOICES = [
        ('goods', 'Goods'),
        ('raw_material', 'Raw Material'),
        ('semi_finished', 'Semi Finished'),
    ]

    name = models.CharField(max_length=100)
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='products')
    hsn_sac = models.CharField(max_length=20)
    statuary_details = models.TextField(blank=True)

    gst_applicable = models.BooleanField(default=True)
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    freight_applicable = models.BooleanField(default=False)
    freight_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    type_of_supply = models.CharField(max_length=20, choices=SUPPLY_TYPE_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
        


class PartyGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Party(models.Model):
    group = models.ForeignKey(PartyGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20)
    address = models.TextField()
    location = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class Voucher(models.Model):
    VOUCHER_TYPE_CHOICES = [
        ('buyer', 'Buyer Voucher'),
        ('seller', 'Seller Voucher'),
        ('jobwork', 'Job Work Challan'),
        ('delivery', 'Delivery Challan'),
        ('quotation', 'Quotation'),
    ]

    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_voucher_type_display()} #{self.id} for {self.party.name}"

class VoucherItem(models.Model):
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    hsn_code = models.CharField(max_length=20)
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2)

    def total_price(self):
        base = self.unit_price * self.quantity
        cgst = base * self.cgst_percent / 100
        sgst = base * self.sgst_percent / 100
        return base + cgst + sgst

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"



class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} - {self.quantity} units"
