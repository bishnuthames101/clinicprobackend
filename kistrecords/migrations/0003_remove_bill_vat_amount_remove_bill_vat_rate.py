# Generated by Django 5.2.1 on 2025-05-29 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kistrecords', '0002_alter_patient_age_alter_patient_last_visit_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='vat_amount',
        ),
        migrations.RemoveField(
            model_name='bill',
            name='vat_rate',
        ),
    ]
