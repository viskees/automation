# Generated by Django 2.2.4 on 2019-10-04 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0010_auto_20191004_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualserver',
            name='profilesslclient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='database.ProfileSSLClient'),
        ),
    ]
