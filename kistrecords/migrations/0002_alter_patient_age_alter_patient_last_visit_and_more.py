# Generated by Django 5.2.1 on 2025-05-29 15:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kistrecords', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='age',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='patient',
            name='last_visit',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.CharField(max_length=100)),
                ('diagnosis', models.CharField(max_length=200)),
                ('treatment', models.TextField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='kistrecords.patient')),
            ],
        ),
        migrations.CreateModel(
            name='MedicalReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('image', 'Image'), ('document', 'Document')], max_length=50)),
                ('fileUrl', models.URLField()),
                ('uploadedBy', models.CharField(max_length=100)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_reports', to='kistrecords.patient')),
            ],
        ),
    ]
