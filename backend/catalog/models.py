from django.db import models
from django.db.models.functions import Lower


def normalize_name(value):
    """Trim, collapse internal whitespace, and leave the operator's casing alone.

    B6 FR-019 makes a master's name its identity: "Acme", " Acme ", and "Acme  Ltd"
    with a double space are the same supplier typed carelessly, not three suppliers.
    Display text is preserved as entered — only the comparison is normalized, which is
    why casing survives here and the uniqueness constraint is what folds it.
    """
    if not value:
        return value
    return " ".join(str(value).split())


class NormalizedNameModel(models.Model):
    """Shared save-time normalization for the single-name master types."""

    name_field = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        setattr(self, self.name_field, normalize_name(getattr(self, self.name_field)))
        return super().save(*args, **kwargs)


class Category(NormalizedNameModel):
    name_field = "category_name"
    category_name = models.CharField(unique=True, max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(Lower('category_name'),
                                               name='uniq_category_name_ci')]

    def __str__(self):
        return self.category_name


class Brand(NormalizedNameModel):
    name_field = "brand_name"
    brand_name = models.CharField(unique=True, max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(Lower('brand_name'),
                                               name='uniq_brand_name_ci')]

    def __str__(self):
        return self.brand_name


class Model(NormalizedNameModel):
    """A product model, identified by its Brand together with its name.

    B6 FR-020: a Model belongs to exactly one Brand, and "Latitude" means nothing
    without knowing whose. The Brand is PROTECTed so it cannot be deleted out from
    under the Models that name it.
    """
    name_field = "model_name"
    brand = models.ForeignKey('catalog.Brand', on_delete=models.PROTECT,
                              related_name="models", null=True, blank=True)
    model_name = models.CharField(max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(
            'brand', Lower('model_name'), name='uniq_model_per_brand_ci')]

    def __str__(self):
        return f"{self.brand.brand_name} {self.model_name}" if self.brand_id else self.model_name


class PurchaseMode(NormalizedNameModel):
    name_field = "purchase_mode"
    purchase_mode = models.CharField(unique=True, max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(Lower('purchase_mode'),
                                               name='uniq_purchase_mode_ci')]

    def __str__(self):
        return self.purchase_mode


class Vendor(NormalizedNameModel):
    name_field = "name"
    name = models.CharField(unique=True, max_length=150)
    contact_person = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")

    class Meta:
        constraints = [models.UniqueConstraint(Lower('name'), name='uniq_vendor_name_ci')]

    def __str__(self):
        return self.name
