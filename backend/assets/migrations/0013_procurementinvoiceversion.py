# Generated for CHG-B6-01 on 2026-09-23.
import django.db.models.deletion
from django.db import migrations, models

import assets.models
import assets.storage


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_audit_access_permission'),
        ('assets', '0012_assetcheckout_closed_as_interrupted_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcurementInvoiceVersion',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('file', models.FileField(
                    storage=assets.storage.PrivateInvoiceStorage(),
                    upload_to=assets.models.procurement_invoice_path)),
                ('file_name', models.CharField(max_length=255)),
                ('version', models.PositiveIntegerField()),
                ('is_current', models.BooleanField(default=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('procurement', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='invoice_versions', to='assets.procurement')),
                ('uploaded_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='accounts.user')),
            ],
            options={
                'ordering': ['-version'],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('procurement', 'version'),
                        name='uniq_procurement_invoice_version'),
                    models.UniqueConstraint(
                        condition=models.Q(('is_current', True)),
                        fields=('procurement',),
                        name='uniq_current_invoice_per_procurement'),
                    models.CheckConstraint(
                        condition=models.Q(('version__gte', 1)),
                        name='procurement_invoice_version_positive'),
                ],
            },
        ),
    ]
