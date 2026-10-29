from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('assets', '0017_merge_20261009_1504')]

    operations = [migrations.AlterField(
        model_name='asset', name='status',
        field=models.CharField(default='In Storage', max_length=32),
    )]
