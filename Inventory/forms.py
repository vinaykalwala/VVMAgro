from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm


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

# from django import forms
# from .models import StockExchangeForm, StockExchangeProduct, Voucher, VoucherProduct

# class StockExchangeFormForm(forms.ModelForm):
#     class Meta:
#         model = StockExchangeForm
#         fields = ['operation_type', 'warehouse', 'party', 'description']

# class StockExchangeProductForm(forms.ModelForm):
#     class Meta:
#         model = StockExchangeProduct
#         fields = ['product', 'quantity', 'phase']

# StockExchangeProductFormSet = forms.inlineformset_factory(
#     StockExchangeForm,
#     StockExchangeProduct,
#     form=StockExchangeProductForm,
#     extra=1,
#     can_delete=True
# )

# class VoucherForm(forms.ModelForm):
#     class Meta:
#         model = Voucher
#         fields = ['voucher_type']

# class VoucherProductForm(forms.ModelForm):
#     class Meta:
#         model = VoucherProduct
#         fields = ['product', 'quantity', 'phase']

# VoucherProductFormSet = forms.inlineformset_factory(
#     Voucher,
#     VoucherProduct,
#     form=VoucherProductForm,
#     extra=1,
#     can_delete=True
# )


# from django import forms
# from .models import Product, Warehouse, Party

# MOVEMENT_CHOICES = [('in', 'In'), ('out', 'Out'), ('job_work', 'Job Work')]

# class ProductExchangeForm(forms.Form):
#     product = forms.ModelChoiceField(queryset=Product.objects.all())
#     movement_type = forms.ChoiceField(choices=MOVEMENT_CHOICES)
#     warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
#     party = forms.ModelChoiceField(queryset=Party.objects.all())
#     quantity = forms.DecimalField(max_digits=10, decimal_places=2)

# from .models import Voucher

# class VoucherForm(forms.ModelForm):
#     class Meta:
#         model = Voucher
#         fields = ['voucher_type']

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'group', 'price_per_unit', 'unit_of_measurement', 
                  'stock_quantity', 'warehouse', 'phase']  # <- include phase


from django import forms
from .models import Product, Warehouse, Party, VoucherProductItem, Voucher

class ProductExchangeItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    movement_type = forms.ChoiceField(choices=VoucherProductItem.MOVEMENT_TYPE_CHOICES)
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
class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = ['voucher_type', 'igst_applicable','party','remarks','place_of_supply']  

    def __init__(self, *args, **kwargs):
        allowed_voucher_types = kwargs.pop('allowed_voucher_types', None)
        super().__init__(*args, **kwargs)
        if allowed_voucher_types:
            self.fields['voucher_type'].choices = [
                (k, v) for k, v in Voucher.VOUCHER_TYPES if k in allowed_voucher_types
            ]