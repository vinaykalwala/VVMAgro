from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
import pytz

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
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

    def save(self, *args, **kwargs):
        if not self.code:
            count = Warehouse.objects.count() + 1
            self.code = f'VVMAgroWH_{count:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    SUPPLY_TYPE_CHOICES = [
        ('goods', 'Goods'),
        ('raw_material', 'Raw Material'),
    ]
    PHASE_CHOICES = [
        ('phase_1', 'Phase 1'),
        ('phase_2', 'Phase 2'),
        ('phase_3', 'Phase 3'),
        
    ]
    #Prodct details
    name = models.CharField(max_length=100)
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='products')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_of_measurement = models.CharField(max_length=50)
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    #Statuatory Details

    # HSN/SAC related details
    hsn_sac = models.CharField(max_length=20, help_text="Enter HSN or SAC code")
    hsn_sac_details = models.TextField(blank=True, help_text="Detailed information about the HSN/SAC code")
    hsn_sac_source_of_details = models.CharField(max_length=255, blank=True, help_text="Source from where HSN/SAC info was obtained")
    hsn_sac_description = models.TextField(blank=True, help_text="Description for the HSN/SAC code")


    type_of_supply = models.CharField(max_length=20, choices=SUPPLY_TYPE_CHOICES)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def created_at_ist(self):
        """Return created_at converted to Indian Standard Time (IST)."""
        if self.created_at:
            ist = pytz.timezone('Asia/Kolkata')
            return self.created_at.astimezone(ist)
        return None

    def __str__(self):
        return self.name
        


class PartyGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Party(models.Model):
    group = models.ForeignKey(PartyGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    gstin_uin_number = models.CharField(max_length=20)
    address = models.TextField()
    location = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    state=models.CharField(max_length=20)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

from django.db import models
from datetime import datetime

class Voucher(models.Model):
    VOUCHER_TYPES = [
        ('Buyer_Voucher', 'Buyer Voucher'),
        ('Seller_Voucher', 'Seller Voucher'),
        ('Job_Work_Voucher', 'Job Work Voucher'),
        ('Quotation', 'Quotation'),
        ('Delivery_Challan', 'Delivery Challan'),
    ]
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'In'),
        ('out', 'Out'),
        ('job_work', 'Job Work'),
    ]

    voucher_number = models.CharField(max_length=30, blank=True)
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPES)
    created_at = models.DateTimeField(default=datetime.now)  # Editable manually
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES, default='in')

    party = models.ForeignKey('Party', on_delete=models.CASCADE)
    place_of_supply = models.CharField(max_length=100, blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)

    freight_applicable = models.BooleanField(default=False)
    freight_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # For Quotation & Delivery Challan
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    reference_date = models.DateField(blank=True, null=True)

    # Totals (auto-calculated)
    total_subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_cgst = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_sgst = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_igst = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.party and not self.place_of_supply:
            self.place_of_supply = self.party.state_name

        if not self.voucher_number:
            now = datetime.now()
            fy_start = now.year if now.month >= 4 else now.year - 1
            fy_end = fy_start + 1
            fy_str = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
            prefix = f"VVMAgro/{fy_str}/{self.voucher_type}/"
            count = Voucher.objects.filter(voucher_number__startswith=prefix).count() + 1
            self.voucher_number = f"{prefix}{str(count).zfill(3)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.voucher_number} - {self.get_voucher_type_display()}"

class VoucherProductItem(models.Model):

    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)


    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)

    # GST in percentages (from Product model)
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    igst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # GST calculated amounts
    cgst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    igst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity} ({self.voucher.voucher_number})"


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100, default="Hyderabad, Telangana")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField(blank=True)
    portfolio_link = models.URLField(blank=True, null=True)  
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job.title}"
class Contact(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


