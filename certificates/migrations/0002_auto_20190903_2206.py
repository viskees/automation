# Generated by Django 2.2.4 on 2019-09-03 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bigipnodes',
            old_name='node_ip',
            new_name='bigip_ip',
        ),
        migrations.RenameField(
            model_name='bigipnodes',
            old_name='node_name',
            new_name='bigip_name',
        ),
        migrations.RenameField(
            model_name='certificates',
            old_name='bigip_node',
            new_name='bigip_name',
        ),
    ]