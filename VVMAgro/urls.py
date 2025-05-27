from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Inventory.models import *
from Inventory.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home, name='home'),
    path('aboutus/',aboutus, name='aboutus'),
    path('products/',products, name='products'),
    path('front-dozer-tractor/', front_dozer_tractor, name='front_dozer_tractor'),
    path('products/hydraulicboomlift/', hydraulicboomlift, name='hydraulicboomlift'),
    path('frontendloader/', frontendloader, name='frontendloader'),
    path('lift-tractor/', lift_tractor, name='lift_tractor'),
    path('hole-digger/', hole_digger, name='hole_digger'),

    path('branchesanddistributors',branchesanddistributors, name='branchesanddistributors'),
    path('careers/',careers, name='careers'),
    path('tractorfarming/',tractorproducts, name='tractorproducts'),
    path('pesticidesprayer/',pesticideprayer,name='pesticidesprayer'),
  
    path('branchesanddistributors/',branchesanddistributors, name='branchesanddistributors'),
    path('careers/',careers, name='careers'),
    path('contacts/', contact_list_view, name='contact_list'),
    path('contacts/new/', contact_create_view, name='contact_create'),
    path('tractorfarming/',tractorproducts, name='tractorproducts'),
    path('pesticidesprayer/',pesticideprayer,name='pesticidesprayer'),

    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
    path('product-exchange/', product_exchange_view, name='product_exchange'),
    path('voucher/create/', voucher_create_view, name='voucher_create'),
    path('vouchers/', voucher_list_view, name='voucher_list'),
    path('voucher/<int:voucher_id>/',voucher_detail_view, name='voucher_detail'),

    # ProductGroup
    path('productgroups/', productgroup_list, name='productgroup_list'),
    path('productgroups/create/', productgroup_create, name='productgroup_create'),
    path('productgroups/<int:pk>/update/', productgroup_update, name='productgroup_update'),
    path('productgroups/<int:pk>/delete/', productgroup_delete, name='productgroup_delete'),

    # Warehouse
    path('warehouses/', warehouse_list, name='warehouse_list'),
    path('warehouses/create/', warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/update/', warehouse_update, name='warehouse_update'),
    path('warehouses/<int:pk>/delete/', warehouse_delete, name='warehouse_delete'),

    # Product
    path('productslist/', product_list, name='product_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/<int:pk>/update/', product_update, name='product_update'),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),

    # PartyGroup
    path('partygroups/', partygroup_list, name='partygroup_list'),
    path('partygroups/create/', partygroup_create, name='partygroup_create'),
    path('partygroups/<int:pk>/update/', partygroup_update, name='partygroup_update'),
    path('partygroups/<int:pk>/delete/', partygroup_delete, name='partygroup_delete'),

    # Party
    path('parties/', party_list, name='party_list'),
    path('parties/create/', party_create, name='party_create'),
    path('parties/<int:pk>/update/', party_update, name='party_update'),
    path('parties/<int:pk>/delete/', party_delete, name='party_delete'),

    # JobApplication
    path("apply/<int:job_id>/", apply_for_job, name="apply_for_job"),
    path('post/', job_post_view, name='job_post'),
    path('applications/', job_applications_view, name='job_applications'),
    path('applications/<int:application_id>/', application_detail_view, name='application_detail'),

    path('stock-report/', stock_report_view, name='stock_report'),
    path('day-book/', day_book_view, name='day_book'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)