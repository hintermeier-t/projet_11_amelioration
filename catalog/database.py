"""
The database module :

This module is called when "python manage.py populate_db" is called. This
module downloads (by request) and install (via PostgreSQL) the
products-related database (products, categories...).

"""

import requests
from . import models


class Database:
    """
    The Database class will request the data to OpenFoodFacts, clean and save
    to the database.
    
    Attributes:
    -----------
    :self.url_cat (string): url to fetches OpenFoodFacts categories;
    :self.url_prod (string): ur to fetches OpenFoodFacts products;
    :self.prod (list): products list;
    :self.cat (list): categories list.

    Methods:
    --------
    :fetch_categories(self): lists all OFF categories;
    :fetch_products(self): lists all OFF products;
    :fill_database(self): uses all fetched objects to fill in the database.
    """

    def __init__(self):
        """
        Init method
        """
        
        self.url_cat = "https://fr.openfoodfacts.org/categories.json"
        self.url_prod = "https://fr.openfoodfacts.org/langue/francais.json"
        self.prod = []
        self.cat = []

    def fetch_categories(self):
        """Stores the categories in a list.

        Fetches all categories starting with a capital letter (to avoid
        irrelevant names starting by 'fr:', 'en:', 'ar': etc...).

        """

        response = requests.request("GET", self.url_cat)
        for each in response.json()["tags"]:
            # - For each 'tag', we save the category name
            if each["name"][0].isupper():
                self.cat.append(each["name"])

    def fetch_products(self):
        """Stores 20 000 products in a list.
        Fetches the 20 000 most searched products in the French products.
        """

        self.request_params = {
            "action": "process",
            # -  We chose the most wanted products
            "sort_by": "unique_scans_n",
            "page_size": 1000,
            "page": 0,
            # -  We'll need a json to process the data
            "json": 1,
        }
        try:

            for index in range(0, 20):
                self.request_params["page"] = index + 1
                query = requests.get(self.url_prod, self.request_params)
                if query.status_code == 200:  # -  if success
                    self.prod.extend(query.json()["products"])

        except requests.ConnectionError:
            print("Unable to Connect to {0}".format(self.url_prod))

    def fill_database(self):
        """
        Fills the database with products and categories
        """

        for category in self.cat:
            try:
                models.Category.objects.create(name=category)
            except:
                pass

        for product in self.prod:
            try:
                new_product = models.Product.objects.create(
                    name=product.get("product_name_fr"),
                    brand=product.get("brands"),
                    code=product.get("code"),
                    nutriscore=product.get("nutriscore_grade").upper(),
                    description=product.get("generic_name_fr"),
                    picture=product.get("image_url"),
                    url=product.get("url"),
                )
                categories = [cat for cat in product.get("categories").split(",")]
                for each in categories:
                    try:
                        new_product.categories.add(
                            models.Category.objects.get(name=each)
                        )
                    except:
                        pass
                new_product.save()
            except:
                pass
