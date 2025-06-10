from django.db.models import F
from .models import Product

def low_stock_count(request):
    if request.user.is_authenticated:
        count = Product.objects.filter(stock_quantity__lt=F('stock_limit')).count()
        return {'low_stock_count': count}
    return {}
