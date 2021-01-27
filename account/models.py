from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from catalog.models import Product
from django.contrib.auth.models import User


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Favoris"
from django.contrib.auth import get_user_model

class EmailBackend(object):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        else:
            if getattr(user, 'is_active', False) and  user.check_password(password):
                return user
        return None
    def get_user(self, user_id):
        User = get_user_model()        
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None