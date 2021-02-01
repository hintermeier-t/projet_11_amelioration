""" Catalog's views module.
Every app view is called here.
"""

#- Django Modules
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

#- Custom modules
from .models import Product, Comment
from .forms import CommentSubmitForm


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
    if request.method == "POST":
        form = CommentSubmitForm(request.POST)
        if form.is_valid():
            Comment.object.create(
                user = request.user.id,
                product = product_id,
                content = request.POST.get('Commentaire'),
                date = timezone.now()
            )
    else:
        form = CommentSubmitForm()
        product = get_object_or_404(Product, pk=product_id)
        categories = " ".join(
            [category.name for category in product.categories.all()]
            )
        comments = Comment.objects.filter(
            product = product_id,
            validated=True)
        context = {
            "product_name": product.name,
            "nutriscore": product.nutriscore,
            "description": product.description,
            "brand": product.brand,
            "thumbnail": product.picture,
            "url": product.url,
            "categories":categories,
            "comments": comments,
            "form": form
        }

    return render(request, "catalog/detail.html", context)


def legal(request):
    """
    Legal page view.
    """
    context = {}
    return render(request, "catalog/legal.html", context)
