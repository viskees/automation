# Generated by Django 2.2.4 on 2019-09-25 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0007_certificates_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificates',
            name='full_name',
        ),
    ]