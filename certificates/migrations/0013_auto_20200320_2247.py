# Generated by Django 2.2.4 on 2020-03-20 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0012_auto_20200320_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='certserversslvirtualserver',
            name='cert_common_name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certserversslvirtualserver',
            name='cert_san',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certserversslvirtualserverviairuleanddatagroup',
            name='cert_common_name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certserversslvirtualserverviairuleanddatagroup',
            name='cert_san',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
