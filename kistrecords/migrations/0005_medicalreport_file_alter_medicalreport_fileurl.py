# Generated by Django 5.2.1 on 2025-05-30 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kistrecords', '0004_alter_bill_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalreport',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='medical_reports/'),
        ),
        migrations.AlterField(
            model_name='medicalreport',
            name='fileUrl',
            field=models.URLField(blank=True, null=True),
        ),
    ]
