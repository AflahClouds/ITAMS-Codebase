from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0006_backfill_amc_contract"),
    ]

    operations = [
        migrations.RemoveField(model_name="asset", name="has_amc"),
        migrations.RemoveField(model_name="asset", name="amc_start"),
        migrations.RemoveField(model_name="asset", name="amc_end"),
        migrations.RemoveField(model_name="asset", name="amc_status"),
        migrations.RemoveField(model_name="asset", name="amc_end_reason"),
    ]
