"""Attach each existing Model to the Brand its Assets actually use (B6 FR-020).

Model identity is the Brand plus the name, but the column did not exist until now, so
every existing row has to be placed. The Assets that reference a Model already record a
Brand, and that is real evidence rather than a guess — where every Asset using a Model
agrees on the Brand, the Model belongs to it.

Where they disagree, or where no Asset uses the Model at all, the Brand is left empty.
Inventing one would be worse than leaving the gap visible: it would put a supplier's
name against a product on no evidence. Those rows are reported by the conformance suite
and are a data-cleanup task, not something a migration should decide.
"""
from django.db import migrations


def backfill(apps, schema_editor):
    Model = apps.get_model("catalog", "Model")
    Asset = apps.get_model("assets", "Asset")

    for model in Model.objects.filter(brand__isnull=True):
        brands = set(
            Asset.objects.filter(model_id=model.pk)
            .values_list('brand_id', flat=True)
            .distinct()
        )
        brands.discard(None)
        if len(brands) == 1:
            model.brand_id = brands.pop()
            model.save(update_fields=['brand'])


def unbackfill(apps, schema_editor):
    Model = apps.get_model("catalog", "Model")
    Model.objects.update(brand=None)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_model_brand_alter_model_model_name_and_more"),
        ("assets", "0011_procurementarrival_procurementassetlink_and_more"),
    ]

    operations = [migrations.RunPython(backfill, unbackfill)]
