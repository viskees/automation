# Generated by Django 2.2.4 on 2020-01-03 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0021_auto_20200102_1613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificates',
            name='profile_ssl_server',
        ),
        migrations.AddField(
            model_name='profilesslclient',
            name='certs',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
