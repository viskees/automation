# Generated by Django 2.2.4 on 2020-01-03 08:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0022_auto_20200103_0825'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profilesslclient',
            old_name='certs',
            new_name='certs_names',
        ),
    ]
