from django.db import models


class Category(models.Model):
    category_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.brand_name


class Model(models.Model):
    model_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.model_name


class PurchaseMode(models.Model):
    purchase_mode = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.purchase_mode
