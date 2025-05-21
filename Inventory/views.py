from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'staticpages/home.html')

def aboutus(request):
    return render(request,'staticpages/aboutus.html')    

def products(request):
    return render(request,'staticpages/products.html')

def tractor(request):
    return render(request, 'staticpages/tractor.html')

def land_smoothing(request):
    return render(request, 'staticpages/land_smoothing.html')

def rice_filtering(request):
    return render(request, 'staticpages/rice_filtering.html')
    
def pesticide_view(request):
    return render(request, 'staticpages/pesticide.html')

def crop_harvester(request):
    return render(request, 'staticpages/crop_harvester.html')

def irrigation_system(request):
    return render(request, 'staticpages/irrigation_system.html')

def branchesanddistributors(request):
    return render(request,'staticpages/branchesanddistributors.html')

def careers(request):
    return render(request,'staticpages/careers.html')

def contactus(request):
    return render(request,'staticpages/contactus.html')  

def tractorproducts(request):
    return render(request,'staticpages/farmingtractor.html')  

def pesticideprayer(request):
    return render(request,'staticpages/pesticidesprayer.html')    

def ricefiltering(request):
    return render(request,'staticpages/ricefiltering.html')        
    return render(request,'staticpages/contactus.html')                


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'backendpages/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on role
                if user.role == 'admin' or user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('user_dashboard')
        else:
            # Invalid login
            return render(request, 'backendpages/login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = CustomAuthenticationForm()
    return render(request, 'backendpages/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def admin_dashboard(request):
    return render(request, 'backendpages/admin_dashboard.html',{'user_profile': request.user})

@login_required
def user_dashboard(request):
    return render(request, 'backendpages/user_dashboard.html',{'user_profile': request.user})

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from decimal import Decimal
from .models import Voucher, VoucherProductItem, Product, Warehouse
from .forms import ProductExchangeItemForm, VoucherForm

def product_exchange_view(request):
    ProductFormSet = formset_factory(ProductExchangeItemForm, extra=1)

    if request.method == 'POST':
        formset = ProductFormSet(request.POST, prefix='products')
        if formset.is_valid():
            product_data = []
            for form in formset:
                data = form.cleaned_data
                if data:
                    product_id = data['product'].id  # Get ID from Product instance
                    product_data.append({
                        'product_id': product_id,
                        'movement_type': data['movement_type'],
                        'warehouse_id': data['warehouse'].id,
                        'quantity': float(data['quantity']),  # convert Decimal to float for JSON
                    })
            request.session['product_exchange_data'] = product_data
            return redirect('voucher_create')
    else:
        formset = ProductFormSet(prefix='products')

    # Pass all products to template for JavaScript supply type filtering
    products = Product.objects.all()

    return render(request, 'product_exchange.html', {
        'formset': formset,
        'products': products,
    })

def get_allowed_voucher_types(movement_types):
    # Check if all movement types are the same
    unique_types = set(movement_types)

    if unique_types == {'in'}:
        return ['Seller_Voucher', 'Quotation', 'Delivery_Challan']
    elif unique_types == {'out'}:
        return ['Buyer_Voucher', 'Quotation', 'Delivery_Challan']
    elif unique_types == {'job_work'}:
        return ['Job_Work_Voucher', 'Quotation', 'Delivery_Challan']
    else:
        # Mixed movement types or none, restrict or raise error if needed
        return ['Quotation', 'Delivery_Challan']  # fallback or limited options

from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Warehouse, VoucherProductItem
from .forms import VoucherForm


def voucher_create_view(request):
    product_data = request.session.get('product_exchange_data')
    if not product_data:
        messages.error(request, "No product data found. Please add products first.")
        return redirect('product_exchange')

    movement_types = [item['movement_type'] for item in product_data]
    allowed_voucher_types = get_allowed_voucher_types(movement_types)

    if request.method == 'POST':
        voucher_form = VoucherForm(request.POST, allowed_voucher_types=allowed_voucher_types)
        if voucher_form.is_valid():
            voucher = voucher_form.save()

            total_subtotal = Decimal('0.00')
            total_cgst = Decimal('0.00')
            total_sgst = Decimal('0.00')
            total_igst = Decimal('0.00')

            igst_applicable = voucher.igst_applicable

            for index, item in enumerate(product_data):
                product = Product.objects.get(id=item['product_id'])
                warehouse = Warehouse.objects.get(id=item['warehouse_id'])
                qty = Decimal(item['quantity'])
                price = product.price_per_unit
                subtotal = price * qty

                cgst_amount = sgst_amount = igst_amount = Decimal('0.00')

                if product.gst_applicable:
                    cgst_amount = (subtotal * product.cgst_percent) / 100
                    sgst_amount = (subtotal * product.sgst_percent) / 100
                    if igst_applicable:
                        igst_amount = cgst_amount + sgst_amount
                        cgst_amount = sgst_amount = Decimal('0.00')

                total_amount = subtotal + cgst_amount + sgst_amount + igst_amount

                if voucher.freight_applicable and voucher.freight_charge:
                    total_amount += voucher.freight_charge


                # Get selected phase from form input
                selected_phase = request.POST.get(f'phase_{index}', None)

                # Update product stock and phase if applicable
                if item['movement_type'] == 'job_work' and voucher.voucher_type == 'Job_Work_Voucher':
                    product.stock_quantity += qty
                    if selected_phase in dict(Product.PHASE_CHOICES):
                        product.phase = selected_phase
                elif item['movement_type'] == 'in' and voucher.voucher_type == 'Seller_Voucher':
                    product.stock_quantity += qty
                elif item['movement_type'] == 'out' and voucher.voucher_type == 'Buyer_Voucher':
                    product.stock_quantity -= qty
                # Do not update stock for delivery challan or quotation

                product.save()

                VoucherProductItem.objects.create(
                    voucher=voucher,
                    product=product,
                    movement_type=item['movement_type'],
                    warehouse=warehouse,
                    quantity=qty,
                    price_per_unit=price,
                    subtotal=subtotal,
                    cgst_amount=cgst_amount,
                    sgst_amount=sgst_amount,
                    igst_amount=igst_amount,
                    total_amount=total_amount
                )

                total_subtotal += subtotal
                total_cgst += cgst_amount
                total_sgst += sgst_amount
                total_igst += igst_amount

            voucher.total_subtotal = total_subtotal
            voucher.total_cgst = total_cgst
            voucher.total_sgst = total_sgst
            voucher.total_igst = total_igst
            voucher.grand_total = total_subtotal + total_cgst + total_sgst + total_igst
            voucher.save()

            del request.session['product_exchange_data']

            messages.success(request, f"Voucher #{voucher.id} saved successfully!")
            return redirect('voucher_detail', voucher_id=voucher.id)
    else:
        voucher_form = VoucherForm(allowed_voucher_types=allowed_voucher_types)

    resolved_products = []
    for index, item in enumerate(product_data):
        try:
            product = Product.objects.get(id=item['product_id'])
            warehouse = Warehouse.objects.get(id=item['warehouse_id'])
            resolved_products.append({
                'index': index,
                'name': product.name,
                'movement_type': item['movement_type'],
                'warehouse': warehouse.name,
                'quantity': item['quantity'],
                'phase': product.phase,
            })
        except (Product.DoesNotExist, Warehouse.DoesNotExist):
            continue

    return render(request, 'voucher_create.html', {
        'voucher_form': voucher_form,
        'products': resolved_products,
        'product_phase_choices': Product.PHASE_CHOICES,
    })


from django.shortcuts import render, get_object_or_404
from .models import Voucher
from num2words import num2words

def voucher_detail_view(request, voucher_id):
    voucher = get_object_or_404(Voucher, id=voucher_id)
    items = voucher.items.all()

    # Determine label based on movement_type of first item
    if voucher.voucher_type == 'Delivery_Challan':
        party_label = 'Delivery Challan'
    elif voucher.voucher_type == 'Quotation':
        party_label = 'Quotation'
    else:
        if items.exists():
            movement_type = items.first().movement_type
            if movement_type == 'in':
                party_label = 'Seller'
            elif movement_type == 'out':
                party_label = 'Buyer'
            elif movement_type == 'job_work':
                party_label = 'Vendor'
            else:
                party_label = 'Party'
        else:
            party_label = 'Party'

    total_subtotal = sum(item.subtotal for item in voucher.items.all())
    total_cgst = sum(item.cgst_amount for item in voucher.items.all())
    total_sgst = sum(item.sgst_amount for item in voucher.items.all())
    total_igst = sum(item.igst_amount for item in voucher.items.all())
    grand_total = sum(item.total_amount for item in voucher.items.all())
    amount_in_words = f"Rupees {num2words(grand_total, lang='en_IN').title()} "

    context = {
        'voucher': voucher,
        'items': items,
        'party_label': party_label,
        'total_subtotal': total_subtotal,
        'total_cgst': total_cgst,
        'total_sgst': total_sgst,
        'total_igst': total_igst,
        'grand_total': grand_total,
        'amount_in_words': amount_in_words,
    }
    return render(request, 'voucher_detail.html', context)
