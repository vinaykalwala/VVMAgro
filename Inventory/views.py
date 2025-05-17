from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'staticpages/home.html')

def aboutus(request):
    return render(request,'staticpages/aboutus.html')    

def products(request):
    return render(request,'staticpages/products.html')

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