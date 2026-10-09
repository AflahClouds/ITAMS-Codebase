from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0015_assetcheckout_classification_remarks'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetcheckout', name='source_checkout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='reconstructed_checkouts', to='assets.assetcheckout'),
        ),
        migrations.AddField(
            model_name='assetcheckout', name='source_transfer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='target_checkouts', to='assets.assettransfer'),
        ),
        migrations.AddField(
            model_name='assetcheckout', name='provenance',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AddField(
            model_name='assetcheckout', name='date_basis',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]
