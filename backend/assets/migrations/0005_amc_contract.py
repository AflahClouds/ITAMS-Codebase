import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0004_finalize_procurement_vendor"),
        ("catalog", "0003_vendor"),
    ]

    operations = [
        migrations.CreateModel(
            name="AmcContract",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("status", models.CharField(default="Active", max_length=16)),
                ("end_reason", models.TextField(blank=True, default="")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("asset", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name="amc_contracts", to="assets.asset")),
                ("vendor", models.ForeignKey(blank=True, null=True,
                                             on_delete=django.db.models.deletion.PROTECT,
                                             to="catalog.vendor")),
            ],
        ),
    ]
