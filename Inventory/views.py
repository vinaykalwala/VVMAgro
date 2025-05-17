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