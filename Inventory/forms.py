from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from .models import JobApplication

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False)
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'phone_number', 'profile_pic', 'role', 'password1', 'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        user.original_password = password  
        user.set_password(password)        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    pass

from django import forms
from .models import Product, Warehouse, Party, VoucherProductItem, Voucher

class ProductExchangeItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    movement_type = forms.ChoiceField(choices=Voucher.MOVEMENT_TYPE_CHOICES)
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    quantity = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2)

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        movement_type = cleaned_data.get('movement_type')

        if product and movement_type:
            # Check if product type_of_supply is 'goods' and movement_type is 'jobwork'
            if product.type_of_supply == 'goods' and movement_type == 'job_work':
                raise forms.ValidationError(
                    "If product type of supply is 'Goods', movement type cannot be 'Jobwork'."
                )
        return cleaned_data
# class VoucherForm(forms.ModelForm):
#     class Meta:
#         model = Voucher
#         fields = ['voucher_type', 'igst_applicable','party','freight_applicable','freight_charge','remarks','place_of_supply']  

#     def __init__(self, *args, **kwargs):
#         allowed_voucher_types = kwargs.pop('allowed_voucher_types', None)
#         super().__init__(*args, **kwargs)
#         if allowed_voucher_types:
#             self.fields['voucher_type'].choices = [
#                 (k, v) for k, v in Voucher.VOUCHER_TYPES if k in allowed_voucher_types
#             ]


class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup
        fields = '__all__'

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class PartyGroupForm(forms.ModelForm):
    class Meta:
        model = PartyGroup
        fields = '__all__'

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = '__all__'

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["first_name", "last_name", "email", "phone", "resume", "cover_letter"]

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume:
            if not resume.name.endswith(".pdf"):
                raise forms.ValidationError("Resume must be a PDF file.")
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Resume file size must be under 5MB.")
        return resume
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'company', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'job_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        
from django import forms
from .models import Gallery

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'image', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'role', 'profile_pic']


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password")

from django import forms
from .models import Voucher, VoucherProductItem, Party, Product, Warehouse

from django import forms
from django.forms import inlineformset_factory,BaseInlineFormSet
from .models import Voucher, VoucherProductItem

class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = [
            'voucher_number',
            'created_at',
            'party',
            'movement_type',
            'place_of_supply',
            'remarks',
            'freight_applicable',
            'freight_charge',
            'reference_number',
            'reference_date',
        ]
        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'}),
            'reference_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        voucher_type = kwargs.pop('voucher_type', None)  # expect this from view
        super().__init__(*args, **kwargs)

        if voucher_type:
            # Set initial movement_type and optionally disable input
            if voucher_type == 'Seller_Voucher':
                self.fields['movement_type'].initial = 'in'
            elif voucher_type == 'Buyer_Voucher':
                self.fields['movement_type'].initial = 'out'
            elif voucher_type == 'Job_Work_Voucher':
                self.fields['movement_type'].initial = 'job_work'
            else:
                # Hide or disable field for Quotation or Delivery Challan
                self.fields.pop('movement_type', None)    

class VoucherProductItemForm(forms.ModelForm):
    phase = forms.ChoiceField(
        choices=Product.PHASE_CHOICES,
        required=False,
        label='Phase'
    )
    class Meta:
        model = VoucherProductItem
        fields = [
            'product', 'warehouse', 
            'quantity', 'price_per_unit',
            'cgst_percent', 'sgst_percent', 'igst_percent',
        ]
        widgets = {
            'subtotal': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'cgst_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'sgst_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'igst_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'total_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Optionally, set initial phase if product is preselected
            if 'product' in self.initial:
                try:
                    product = Product.objects.get(id=self.initial['product'])
                    self.fields['phase'].initial = product.phase
                except Product.DoesNotExist:
                    pass

VoucherProductItemFormSet = inlineformset_factory(
    Voucher,
    VoucherProductItem,
    form=VoucherProductItemForm,
    extra=1,
    can_delete=True,
)

VoucherProductItemFormSetNoExtra = inlineformset_factory(
    Voucher, VoucherProductItem,
    form=VoucherProductItemForm,
    extra=0,   # for Edit
    can_delete=True
)
class ProductUploadForm(forms.Form):
    excel_file = forms.FileField()

class PartyUploadForm(forms.Form):
    excel_file = forms.FileField()


from django import forms
from .models import Account, Transaction

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'


from django import forms
from .models import Transaction, Voucher
from datetime import date, datetime

def generate_voucher_number(transaction_type):
    now = datetime.now()
    fy_start = now.year if now.month >= 4 else now.year - 1
    fy_end = fy_start + 1
    fy_str = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
    prefix_map = {
        'payment': 'PMT',
        'receipt': 'R',
        'contra': 'CON',
    }
    prefix = f"VVM/{fy_str}/{prefix_map.get(transaction_type, 'UNK')}/"
    count = Transaction.objects.filter(transaction_voucher_number__startswith=prefix).count() + 1
    return f"{prefix}{count}"

from django import forms
from .models import Transaction, Voucher
from datetime import date
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transaction_voucher_type': forms.HiddenInput(),
            'transaction_voucher_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'party': forms.Select(attrs={'class': 'form-control', 'onchange': 'loadVouchers()'}),
            'voucher': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        voucher_type = kwargs.pop('voucher_type', None)
        super().__init__(*args, **kwargs)

        # Set initial values
        if voucher_type:
            self.fields['transaction_voucher_type'].initial = voucher_type
            self.fields['transaction_voucher_type'].disabled = True
            
            # Generate and set voucher number
            if not self.instance.pk:
                now = datetime.now()
                fy_start = now.year if now.month >= 4 else now.year - 1
                fy_end = fy_start + 1
                fy_str = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
                prefix_map = {
                    'payment': 'PMT',
                    'receipt': 'R',
                    'contra': 'CON',
                }
                prefix = f"VVM/{prefix_map.get(voucher_type, 'UNK')}/{fy_str}/"
                count = Transaction.objects.filter(
                    transaction_voucher_number__startswith=prefix
                ).count() + 1
                self.fields['transaction_voucher_number'].initial = f"{prefix}{count}"

        # Set today's date as default if not set
        if not self.is_bound and not self.instance.pk:
            self.fields['date'].initial = date.today()

        # Hide contra_details unless voucher_type is "contra"
        if voucher_type != 'contra':
            self.fields.pop('contra_details', None)
            self.fields.pop('recipient_account', None)

        # Initialize voucher queryset
        self.fields['voucher'].queryset = Voucher.objects.none()

        # If editing existing transaction
        if self.instance.pk and self.instance.party:
            self.fields['voucher'].queryset = Voucher.objects.filter(party=self.instance.party)

        # If form is being submitted
        if 'party' in self.data:
            try:
                party_id = int(self.data.get('party'))
                self.fields['voucher'].queryset = Voucher.objects.filter(party_id=party_id)
            except (ValueError, TypeError):
                pass  # Invalid input, keep empty queryset


from django import forms
from .models import ProductComponent, Product, ProductGroup

class ProductComponentForm(forms.ModelForm):
    class Meta:
        model = ProductComponent
        fields = ['component_product', 'quantity_used']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Exclude 'Finished Products' group from component choices
        finished_group = ProductGroup.objects.filter(name__iexact='Finished Products').first()
        if finished_group:
            self.fields['component_product'].queryset = Product.objects.exclude(group=finished_group)
        else:
            # Fallback: allow all if group not found
            self.fields['component_product'].queryset = Product.objects.all()
