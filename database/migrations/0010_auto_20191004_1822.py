# Generated by Django 2.2.4 on 2019-10-04 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0009_certificates_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualserver',
            name='profile_1',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='profile_2',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='profile_3',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='profile_4',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='profile_5',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
