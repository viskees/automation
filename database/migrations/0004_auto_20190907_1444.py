# Generated by Django 2.2.4 on 2019-09-07 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_auto_20190907_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='database',
            name='bigip_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.BigIPNodes'),
        ),
    ]
