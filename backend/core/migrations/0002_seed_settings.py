from django.db import migrations


def seed(apps, schema_editor):
    Setting = apps.get_model("core", "Setting")
    if Setting.objects.filter(key="company_name").first() is None:
        Setting.objects.create(key="company_name", value="Cloud Shoe Factory")
    if Setting.objects.filter(key="theme_color").first() is None:
        Setting.objects.create(key="theme_color", value="#0d6efd")


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
