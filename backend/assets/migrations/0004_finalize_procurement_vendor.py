import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0003_backfill_procurement_vendor"),
        ("catalog", "0003_vendor"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="procurement",
            name="vendor_name",
        ),
        migrations.AlterField(
            model_name="procurement",
            name="vendor",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.vendor"),
        ),
    ]
