# Generated by Django 2.2.4 on 2019-09-05 11:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0003_certificates_partition'),
    ]

    operations = [
        migrations.AddField(
            model_name='bigipnodes',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bigipnodes',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='certificates',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
