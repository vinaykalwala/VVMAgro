from django.shortcuts import render
from .models import *
from .forms import *

# Create your views here.
def home(request):
    return render(request,'staticpages/home.html')

def aboutus(request):
    return render(request,'staticpages/aboutus.html')    

def products(request):
    return render(request,'staticpages/products.html')

def front_dozer_tractor(request):
    return render(request, 'staticpages/front_dozer_tractor.html')

def hydraulicboomlift(request):
    return render(request, 'staticpages/hydraulicboomlift.html')

def hole_digger(request):
    return render(request, 'staticpages/hole_digger.html')
    
def frontendloader(request):
    return render(request, 'staticpages/frontendloader.html')

def lift_tractor(request):
    return render(request, 'staticpages/lift_tractor.html')



def branchesanddistributors(request):
    return render(request,'staticpages/branchesanddistributors.html')

def careers(request):
    return render(request,'staticpages/careers.html')

def tractorproducts(request):
    return render(request,'staticpages/farmingtractor.html')  

def pesticideprayer(request):
    return render(request,'staticpages/pesticidesprayer.html')    

    


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signup')
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
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.role == 'user':
                    return redirect('user_dashboard')
                else:
                    return redirect('manager_dashboard')
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

@login_required
def manager_dashboard(request):
    return render(request, 'backendpages/manager_dashboard.html',{'user_profile': request.user})

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

from django.db.models import Q
from datetime import datetime

def voucher_list_view(request):
    vouchers = Voucher.objects.all().order_by('-created_at')

    voucher_number = request.GET.get('voucher_number', '').strip()
    voucher_type = request.GET.get('voucher_type', '').strip()
    party_name = request.GET.get('party_name', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    date_exact = request.GET.get('date_exact', '').strip()

    if voucher_number:
        vouchers = vouchers.filter(voucher_number__icontains=voucher_number)

    if voucher_type:
        vouchers = vouchers.filter(voucher_type=voucher_type)

    if party_name:
        vouchers = vouchers.filter(party__name__icontains=party_name)

    if date_exact:
        try:
            date_exact_obj = datetime.strptime(date_exact, '%Y-%m-%d')
            vouchers = vouchers.filter(created_at__date=date_exact_obj)
        except ValueError:
            pass
    else:
        # Only apply range filters if exact date not specified
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                vouchers = vouchers.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                vouchers = vouchers.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass

    context = {
        'vouchers': vouchers,
        'search_params': {
            'voucher_number': voucher_number,
            'voucher_type': voucher_type,
            'party_name': party_name,
            'date_from': date_from,
            'date_to': date_to,
            'date_exact': date_exact,
        }
    }
    return render(request, 'voucher_list.html', context)


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


from django.shortcuts import render, get_object_or_404, redirect
from .models import ProductGroup, Warehouse, Product, PartyGroup, Party
from .forms import ProductGroupForm, WarehouseForm, ProductForm, PartyGroupForm, PartyForm

# ProductGroup Views
def productgroup_list(request):
    groups = ProductGroup.objects.all()
    return render(request, 'productgroup_list.html', {'groups': groups})

def productgroup_create(request):
    form = ProductGroupForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('productgroup_list')
    return render(request, 'productgroup_form.html', {'form': form})

def productgroup_update(request, pk):
    group = get_object_or_404(ProductGroup, pk=pk)
    form = ProductGroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        return redirect('productgroup_list')
    return render(request, 'productgroup_form.html', {'form': form})

def productgroup_delete(request, pk):
    group = get_object_or_404(ProductGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('productgroup_list')
    return render(request, 'confirm_delete.html', {'object': group})

# Warehouse Views
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse_list.html', {'warehouses': warehouses})

def warehouse_create(request):
    form = WarehouseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('warehouse_list')
    return render(request, 'warehouse_form.html', {'form': form})

def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    form = WarehouseForm(request.POST or None, instance=warehouse)
    if form.is_valid():
        form.save()
        return redirect('warehouse_list')
    return render(request, 'warehouse_form.html', {'form': form})

def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        return redirect('warehouse_list')
    return render(request, 'confirm_delete.html', {'object': warehouse})

# Product Views
def product_list(request):
    products = Product.objects.select_related('group', 'warehouse').all()
    return render(request, 'product_list.html', {'products': products})

def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'confirm_delete.html', {'object': product})

# PartyGroup Views
def partygroup_list(request):
    groups = PartyGroup.objects.all()
    return render(request, 'partygroup_list.html', {'groups': groups})

def partygroup_create(request):
    form = PartyGroupForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('partygroup_list')
    return render(request, 'partygroup_form.html', {'form': form})

def partygroup_update(request, pk):
    group = get_object_or_404(PartyGroup, pk=pk)
    form = PartyGroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        return redirect('partygroup_list')
    return render(request, 'partygroup_form.html', {'form': form})

def partygroup_delete(request, pk):
    group = get_object_or_404(PartyGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('partygroup_list')
    return render(request, 'confirm_delete.html', {'object': group})

# Party Views
def party_list(request):
    parties = Party.objects.all()
    return render(request, 'party_list.html', {'parties': parties})

def party_create(request):
    form = PartyForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('party_list')
    return render(request, 'party_form.html', {'form': form})

def party_update(request, pk):
    party = get_object_or_404(Party, pk=pk)
    form = PartyForm(request.POST or None, instance=party)
    if form.is_valid():
        form.save()
        return redirect('party_list')
    return render(request, 'party_form.html', {'form': form})

def party_delete(request, pk):
    party = get_object_or_404(Party, pk=pk)
    if request.method == 'POST':
        party.delete()
        return redirect('party_list')
    return render(request, 'confirm_delete.html', {'object': party})



from .models import Job, JobApplication
from .forms import JobApplicationForm

def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect("apply_for_job", job_id=job.id)  
        else:
            messages.error(request, "There was an error with your application. Please check the form.")
    else:
        form = JobApplicationForm()

    return render(request, "staticpages/apply.html", {"form": form, "job": job})

def careers(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, "staticpages/careers.html", {"jobs": jobs})
def contact_create_view(request):
    success = False  # Flag to show success message

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm()  # Clear form after submission
    else:
        form = ContactForm()

    return render(request, 'contact_form.html', {'form': form, 'success': success})

def contact_list_view(request):
    contacts = Contact.objects.all().order_by('-created_at')
    return render(request, 'contact_list.html', {'contacts': contacts})

from django.contrib.auth.decorators import login_required
from .forms import JobForm
from .models import JobApplication

@login_required
def job_post_view(request):
    if not (request.user.role == 'manager' or request.user.role == 'user' or request.user.is_superuser):
        messages.error(request, "Only admins can post jobs.")
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job '{job.title}' posted successfully!")
            return redirect('job_applications')
    else:
        form = JobForm()
    
    return render(request, 'backendpages/job_post.html', {'form': form})

@login_required
def job_applications_view(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, "Only admins can view applications.")
        return redirect('user_dashboard')
    
    applications = JobApplication.objects.all().order_by('-applied_at')
    return render(request, 'backendpages/job_applications.html', {'applications': applications})

@login_required
def application_detail_view(request, application_id):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, "Only admins can view application details.")
        return redirect('user_dashboard')
    
    application = get_object_or_404(JobApplication, id=application_id)
    return render(request, 'backendpages/application_detail.html', {'application': application})


from django.db.models import Q

def stock_report_view(request):
    query = request.GET.get('q', '')
    warehouse_id = request.GET.get('warehouse', '')
    phase = request.GET.get('phase', '')
    supply_type = request.GET.get('type_of_supply', '')

    products = Product.objects.select_related('warehouse').all()

    if query:
        products = products.filter(name__icontains=query)

    if warehouse_id:
        products = products.filter(warehouse_id=warehouse_id)

    if phase:
        products = products.filter(phase=phase)

    if supply_type:
        products = products.filter(type_of_supply=supply_type)

    stock_data = []

    for product in products:
        stock_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "type_of_supply": product.get_type_of_supply_display(),
            "stock_quantity": product.stock_quantity,
            "warehouse_name": product.warehouse.name if product.warehouse else "No Warehouse Assigned",
            "warehouse_location": product.warehouse.location if product.warehouse and hasattr(product.warehouse, 'location') else "Location Not Available",
            "phase": product.get_phase_display() if product.type_of_supply == 'goods' else "N/A"
        })

    warehouses = Warehouse.objects.all()

    return render(request, 'stock_report.html', {
        'stock_data': stock_data,
        'warehouses': warehouses,
        'query': query,
        'selected_warehouse': warehouse_id,
        'selected_phase': phase,
        'selected_type': supply_type,
    })


from django.shortcuts import render, get_object_or_404
from .models import Voucher
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils.timezone import make_aware

def day_book_view(request):
    vouchers = Voucher.objects.all().order_by('-created_at')

    # Get filter parameters from GET request
    date = request.GET.get('date')
    week = request.GET.get('week')  # Format: YYYY-Www (e.g., 2025-W21)
    month = request.GET.get('month')  # Format: YYYY-MM
    year = request.GET.get('year')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    voucher_type = request.GET.get('voucher_type')

    # Apply filters
    if date:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        vouchers = vouchers.filter(created_at__date=date_obj)

    if week:
        year_str, week_str = week.split('-W')
        year, week = int(year_str), int(week_str)
        start_of_week = datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w")
        end_of_week = start_of_week + timedelta(days=6)
        vouchers = vouchers.filter(created_at__date__range=[start_of_week.date(), end_of_week.date()])

    if month:
        year, month = map(int, month.split('-'))
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
        vouchers = vouchers.filter(created_at__date__range=[start_of_month.date(), end_of_month.date()])

    if year:
        vouchers = vouchers.filter(created_at__year=year)

    if start_date and end_date:
        start = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end = make_aware(datetime.strptime(end_date, '%Y-%m-%d')) + timedelta(days=1)
        vouchers = vouchers.filter(created_at__range=[start, end])

    if voucher_type:
        vouchers = vouchers.filter(voucher_type=voucher_type)

    context = {
        'vouchers': vouchers,
    }
    return render(request, 'day_book.html', context)
