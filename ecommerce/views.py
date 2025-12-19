from django.shortcuts import render
from store.models import Product


products = Product.objects.all().filter(is_available=True)

context = {
    'products': products
}
def home(request):
    return render(request, 'home.html', context)