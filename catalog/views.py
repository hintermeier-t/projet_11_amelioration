""" Catalog's views module.
Every app view is called here.
"""

#- Django Modules
from django.shortcuts import render, get_object_or_404

#- Custom modules
from .models import Product


def index(request):
    """
    Index page view.
    """
    context = {}
    return render(request, "catalog/index.html", context)

def search(request):
    """
    Search bar view.
    """
    query = request.GET.get("query")
    if not query:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(name__icontains=query)

        if not products.exists():
            products = Product.objects.filter(code__icontains=query)

    title = 'Résultats pour la recherche "{}":'.format(query)
    context = {"products": products, "query": query, "title": title}
    return render(request, "catalog/search.html", context)


def detail(request, product_id):
    """
    Product's detail view.
    """
    product = get_object_or_404(Product, pk=product_id)
    categories = " ".join(
        [category.name for category in product.categories.all()]
        )
    context = {
        "product_name": product.name,
        "nutriscore": product.nutriscore,
        "description": product.description,
        "brand": product.brand,
        "thumbnail": product.picture,
        "url": product.url,
        "categories":categories,
    }

    return render(request, "catalog/detail.html", context)


def legal(request):
    """
    Legal page view.
    """
    context = {}
    return render(request, "catalog/legal.html", context)
