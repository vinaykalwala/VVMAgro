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
    stock_quantity = stock_quantity = models.IntegerField(default=0)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    stock_limit = models.IntegerField(default=0)

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
    registration_type = models.CharField(max_length=50, blank=True)  # Free-text field


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

    voucher_number = models.CharField(max_length=50, blank=True)
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
    round_off_on_sales=models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
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
        return f"{self.voucher_number}"

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


    

class Gallery(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title


from django.db import models
from datetime import datetime

class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('overdraft', 'Overdraft'),
        ('cash_credit', 'Cash Credit'),
        ('other', 'Other'),
    ]

    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=20)
    account_number = models.CharField(max_length=50, unique=True)
    account_holder_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

from django.db import models
from datetime import datetime, date
from django.core.exceptions import ValidationError

class Transaction(models.Model):
    TRANSACTION_VOUCHER_TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('contra', 'Contra'),
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('Cash', 'Cash'),
        ('Cheque/DD', 'Cheque/DD'),
        ('Card', 'Card'),
        ('ECS', 'ECS'),
        ('E-Fund Transfer', 'E-Fund Transfer'),
        ('Electronic Cheque', 'Electronic Cheque'),
        ('Electronic DD/PO', 'Electronic DD/PO'),
        ('Others', 'Others'),
    ]

    METHOD_OF_ADJUSTMENT_CHOICES = [
        ('Advance', 'Advance'),
        ('Agst Ref', 'Against Reference'),
        ('New Ref', 'New Reference'),
        ('On Account', 'On Account'),
    ]

    transaction_voucher_number = models.CharField(max_length=100, blank=True, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=date.today, blank=True, null=True)

    transaction_voucher_type = models.CharField(max_length=10, choices=TRANSACTION_VOUCHER_TYPE_CHOICES)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    method_of_adjustment = models.CharField(max_length=20, choices=METHOD_OF_ADJUSTMENT_CHOICES)

    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    recipient_account = models.ForeignKey('Account',on_delete=models.SET_NULL,null=True,blank=True,related_name='received_contra_transactions',help_text="Applicable only for Contra transactions")
    party = models.ForeignKey('Party', on_delete=models.SET_NULL, null=True, blank=True)

    contra_details = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter details for Contra transactions"
    )

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    voucher = models.ForeignKey('Voucher', on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Check if sufficient balance is available before saving
        if self.pk is None:  # Only validate on new transactions
            if self.transaction_voucher_type in ['payment', 'contra']:
                if self.account.available_balance < self.amount:
                    raise ValidationError("Insufficient balance in the selected account.")

            if self.transaction_voucher_type == 'contra':
                if not self.recipient_account or self.recipient_account == self.account:
                    raise ValidationError("For contra transactions, recipient_account must be set and different from account.")


    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_instance = None

        if not is_new:
            old_instance = Transaction.objects.get(pk=self.pk)

        if not self.transaction_voucher_number:
            now = datetime.now()
            fy_start = now.year if now.month >= 4 else now.year - 1
            fy_end = fy_start + 1
            fy_str = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
            prefix_map = {
                'payment': 'PMT',
                'receipt': 'R',
                'contra': 'CON',
            }
            prefix = f"VVM/{prefix_map.get(self.transaction_voucher_type, 'UNK')}/{fy_str}/"
            count = Transaction.objects.filter(transaction_voucher_number__startswith=prefix).count() + 1
            self.transaction_voucher_number = f"{prefix}{count}"

        # ===== REVERSE OLD EFFECTS IF UPDATING =====
        if old_instance:
            if old_instance.transaction_voucher_type == 'payment':
                old_instance.account.available_balance += old_instance.amount
                old_instance.account.save()

            elif old_instance.transaction_voucher_type == 'receipt':
                old_instance.account.available_balance -= old_instance.amount
                old_instance.account.save()

            elif old_instance.transaction_voucher_type == 'contra':
                # Reverse from both accounts
                old_instance.account.available_balance += old_instance.amount
                old_instance.account.save()

                if old_instance.recipient_account:
                    old_instance.recipient_account.available_balance -= old_instance.amount
                    old_instance.recipient_account.save()

        # ===== APPLY NEW EFFECTS =====
        if self.transaction_voucher_type == 'payment':
            self.account.available_balance -= self.amount
            self.account.save()

        elif self.transaction_voucher_type == 'receipt':
            self.account.available_balance += self.amount
            self.account.save()

        elif self.transaction_voucher_type == 'contra':
            if not self.recipient_account or self.recipient_account == self.account:
                raise ValueError("For contra transactions, recipient_account must be set and different from account.")

            self.account.available_balance -= self.amount
            self.account.save()

            self.recipient_account.available_balance += self.amount
            self.recipient_account.save()

        super().save(*args, **kwargs)


        def __str__(self):
            return f"{self.transaction_voucher_number} - {self.get_transaction_voucher_type_display()}"


class ProductComponent(models.Model):
    finished_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='components')
    component_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='used_in')
    quantity_used = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.component_product.name} in {self.finished_product.name}"
