# Generated by Django 2.2.4 on 2019-09-25 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0008_remove_certificates_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificates',
            name='full_name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
