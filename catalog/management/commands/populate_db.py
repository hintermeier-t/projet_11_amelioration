"""
Module called with :
> python manage.py populate_db

Calls the database.py module and construct the Products database
"""

from django.core.management.base import BaseCommand

from catalog import database as db


class Command(BaseCommand):
    def handle(self, *args, **options):
        database = db.Database()
        database.fetch_categories()
        database.fetch_products()
        database.fill_database()
