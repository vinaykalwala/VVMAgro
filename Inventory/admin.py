from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ProductGroup)
admin.site.register(Product)
admin.site.register(PartyGroup)
admin.site.register(Party)
admin.site.register(Warehouse)
admin.site.register(Voucher)
admin.site.register(VoucherProductItem)
# admin.site.register(StockExchangeProduct)
# admin.site.register(StockExchangeForm)
