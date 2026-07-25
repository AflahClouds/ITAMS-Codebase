from django.db import migrations

CATEGORIES = ["Laptop", "Desktop", "Printer", "Mobile", "Tablet", "Network Device",
              "Server", "CCTV", "Software License", "Accessories", "Others"]


def seed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    for name in CATEGORIES:
        Category.objects.get_or_create(category_name=name)


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
