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
    path('tractorfarming',tractorproducts, name='tractorproducts'),
    path('pesticidesprayer',pesticideprayer,name='pesticidesprayer'),
    path('ricefiltering',ricefiltering,name='ricefiltering'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)