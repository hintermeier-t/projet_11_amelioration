from django.db import models


class Category(models.Model):
    name = models.CharField("Nom", max_length=75, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Nom", max_length=200)
    brand = models.CharField("Marque", max_length=200)
    code = models.CharField("Code barre", max_length=13)
    nutriscore = models.CharField("Nutriscore", max_length=1)
    description = models.TextField("Description", blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name="Catégories", blank=True)
    picture = models.URLField()
    url = models.URLField()
