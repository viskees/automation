# Generated by Django 2.2.4 on 2019-09-06 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0005_certificates_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificates',
            name='expiration',
            field=models.CharField(default='default', max_length=200),
            preserve_default=False,
        ),
    ]
