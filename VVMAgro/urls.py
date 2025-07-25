from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Inventory.models import *
from Inventory.views import *
from django.conf.urls import handler404, handler500


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
    path('manager_dashboard/', manager_dashboard, name='manager_dashboard'),
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
    
    #Gallery
    path('gallery/', gallery, name='gallery'),
    path('gallery_list/', gallery_list, name='gallery_list'),
    path('gallery_create/', gallery_create, name='gallery_create'),
    path('gallery_edit/<int:pk>/', gallery_edit, name='gallery_edit'),
    path('gallery_delete/<int:pk>/', gallery_delete, name='gallery_delete'),

    
    path('users/', user_list, name='user_list'),
    path('users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('users/<int:user_id>/change-password/', change_user_password, name='change_user_password'),
    path('low-stock/', notify_low_stock_products, name='low_stock_products'),

    path('voucher-types/', voucher_type_list, name='voucher_type_list'),
    path('voucher/create/<str:voucher_type>/', create_voucher_with_items, name='create_voucher_with_items'),
    path('voucher/<int:voucher_id>/edit/', edit_voucher_with_items, name='edit_voucher_with_items'),
    path('voucher/delete/<int:voucher_id>/', delete_voucher, name='delete_voucher'),
    path('upload-products/', upload_products, name='upload_products'),
    path('upload-parties/', upload_parties, name='upload_parties'),

    path('accounts/', account_list, name='account_list'),
    path('accounts/create/', account_create, name='account_create'),
    path('accounts/<int:pk>/edit/', account_update, name='account_update'),
    path('accounts/<int:pk>/delete/', account_delete, name='account_delete'),

    # Transactions
    path('transactions/',transaction_list, name='transaction_list'),
    path('transactions/select-type/', select_transaction_type, name='select_transaction_type'),
    path('transactions/create/<str:voucher_type>/', transaction_create, name='transaction_create'),
    path('transaction/edit/<int:pk>/', transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/', transaction_detail, name='transaction_detail'),
    path('transaction/delete/<int:pk>/', delete_transaction, name='delete_transaction'),
    path('ajax/load-vouchers/', LoadVouchersView.as_view(), name='load_vouchers'),
    path('ajax/get-account-balance/', get_account_balance, name='get_account_balance'),
    path('accounts/<int:account_id>/history/', account_transaction_history, name='account_transaction_history'),
    path('products/<int:pk>/add-stock/', add_finished_product_stock, name='add_finished_product_stock'),
    path('export-sales-summary/<int:year>/<int:month>/', export_sales_summary_excel, name='export_sales_summary'),
    path('download-sales-summary/', download_sales_summary_page, name='download_sales_summary_page'),
    path('export/hsn-summary-form/', hsn_summary_form, name='hsn_summary_form'),
    path('export/hsn-summary/<int:year>/<int:month>/', export_hsn_gst_summary_excel, name='export_hsn_gst_summary'),
    path('export/products/', export_products_excel, name='export_products_excel'),
    path('export/party/', export_party_excel, name='export_party_excel'),
    path('profit-loss/', profit_loss_report, name='profit_loss_report'),





]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'Inventory.views.custom_404_view'
handler500 = 'Inventory.views.custom_500_view'