from django.urls import path

from . import views


urlpatterns = [
    path("search/", views.search, name="search"),
    path("<int:product_id>/", views.detail, name="detail"),
    path("legal/", views.legal, name="legal"),
]

app_name = "catalog"
