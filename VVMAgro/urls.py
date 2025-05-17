from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Inventory.models import *
from Inventory.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home, name='home'),
    path('aboutus',aboutus, name='aboutus'),
    path('products',products, name='products'),
    path('branchesanddistributors',branchesanddistributors, name='branchesanddistributors'),
    path('careers',careers, name='careers'),
    path('contactus',contactus, name='contactus'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
    path('product-exchange/', product_exchange_view, name='product_exchange'),
    path('voucher/create/', voucher_create_view, name='voucher_create'),
    path('voucher/<int:voucher_id>/',voucher_detail_view, name='voucher_detail'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)