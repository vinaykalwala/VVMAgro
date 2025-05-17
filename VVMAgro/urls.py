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
    path('tractor/', tractor, name='tractor'),
    path('products/land-smoothing/', land_smoothing, name='land_smoothing'),
    path('pesticide/', pesticide_view, name='pesticide'),
    path('crop-harvester/', crop_harvester, name='crop_harvester'),
    path('rice-filtering/', rice_filtering, name='rice_filtering'),
    path('irrigation-system/', irrigation_system, name='irrigation_system'),
    path('branchesanddistributors',branchesanddistributors, name='branchesanddistributors'),
    path('careers',careers, name='careers'),
    path('contactus',contactus, name='contactus'),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)