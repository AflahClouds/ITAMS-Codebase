from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0007_remove_asset_amc_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="amccontract",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="amccontract",
            name="end_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
