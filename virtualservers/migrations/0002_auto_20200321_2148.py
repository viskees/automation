# Generated by Django 2.2.4 on 2020-03-21 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtualservers', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VirtualServer',
            new_name='VirtualServerCluster',
        ),
    ]
