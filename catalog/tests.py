"""
Testing module for the 'catalog' app only. Each test sequence is contained
within a class. Each test of the sequence is a class method.
"""

from django.test import TestCase
from django.urls import reverse

from .models import Product, Category


# - Index page
class IndexPageTestCase(TestCase):
    """
    Testing index view.
    """

    # - Index page returns 200
    def test_index_page(self):
        """
        Accessing index view.

        Returns 200.
        """
        request = self.client.get(reverse("index"))
        self.assertEqual(request.status_code, 200)

# - Detail page
class DetailPageTestCase(TestCase):
    """
    Testing detail view.
    
    Attributes (setUp method) :
    ---------------------------
    :self.product (Product): a Product to find

    Tests:
    ------
    :test_detail_page_200(self): Request a Product's details.
    :test_detail_page_204(self): Request a non existing Product's detail.
        credentials.
    """

    def setUp(self):
        """
        Tests setup.
        """

        product_test = Product.objects.create(
            name="Produit à manger",
            brand="Chuipariche",
            code="1234567890123",
            nutriscore="B",
            description="C'est bon à cuisiner",
            picture="truc.com/image.jpg",
            url="truc.com/fiche.html",
        )
        self.product = Product.objects.get(name="Produit à manger")

    # - If item exists : returns 200
    def test_detail_page_200(self):
        """
        Conditions:
        -----------
        *Product does exist.

        Assertions:
        -----------
        *Status Code = 200.
        """

        product_id = self.product.id
        request = self.client.get(reverse("catalog:detail", args=(product_id,)))
        self.assertEqual(request.status_code, 200)

    # - If item does not exist : returns 404
    def test_detail_page_404(self):
        """
        Conditions:
        -----------
        *Product does not exist.

        Assertions:
        -----------
        *Status Code = 404.
        """
        
        product_id = self.product.id + 1
        request = self.client.get(reverse("catalog:detail", args=(product_id,)))
        self.assertEqual(request.status_code, 404)


# - Legal page
class LegalPageTestCase(TestCase):
    """
    Testing legal view.
    """

    # - Returns 200
    def test_legal_page(self):
        """
        Accessing legal page.

        Returns 200.
        """

        request = self.client.get(reverse("legal"))
        self.assertEqual(request.status_code, 200)


# - Search function
class SearchPageTestCase(TestCase):
    """
    Testing search view.
    
    Attributes (setUp method) :
    ---------------------------
    :self.product_one (Product): a Product to find;
    :self.product_two (Product): another Product to find.

    Tests:
    ------
    :test_search_without_query(self): Enter an empty form;
    :test_search_with_name_query(self): Request a Product by its name;
    :test_search_with_code_query(self): Request a Product by its barcode.
        credentials.
    """

    def setUp(self):
        """
        Tests setup.
        """

        self.product_one = Product.objects.create(
            name="Produit à manger",
            brand="Chuipariche",
            code="1234567890123",
            nutriscore="B",
            description="C'est bon à cuisiner",
            picture="truc.com/image.jpg",
            url="truc.com/fiche.html",
        )
        self.product_two = Product.objects.create(
            name="Produit de luxe",
            brand="Monopolprix",
            code="9876543210987",
            nutriscore="A",
            description="Cuisiné par les grands",
            picture="truc.com/image.jpg",
            url="truc.com/fiche.html",
        )

    # - Without query, returns all products
    def test_search_without_query(self):
        """
        Conditions:
        -----------
        *No product found

        Assertions:
        -----------
        *Status Code = 200;
        * All Product objects returned (2).
        """

        request = self.client.get(reverse("catalog:search"))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context["products"]),
            Product.objects.count()
            )

    # - Test with a name passed as query
    def test_search_with_name_query(self):
        """
        Conditions:
        -----------
        *Product does exist.

        Assertions:
        -----------
        *Status Code = 200;
        *Only one Product returned;
        *The right Product is returned.
        """

        request = self.client.get(
            reverse("catalog:search"), {"query": "Produit à manger"}
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context["products"]), 1)
        product = Product.objects.get(name="Produit à manger")
        self.assertEqual(request.context["products"][0].id, product.id)

    # - Test with a code passed as query
    def test_search_with_code_query(self):
        """
        Conditions:
        -----------
        *Product does exist.

        Assertions:
        -----------
        *Status Code = 200;
        *Only one Product returned;
        *The right Product is returned.
        """

        request = self.client.get(reverse("catalog:search"),
            {"query": "9876543210987"}
            )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context["products"]), 1)
        product = Product.objects.get(code="9876543210987")
        self.assertEqual(request.context["products"][0].id, product.id)
