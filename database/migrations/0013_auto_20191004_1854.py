# Generated by Django 2.2.4 on 2019-10-04 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0012_auto_20191004_1831'),
    ]

    operations = [
        migrations.RenameField(
            model_name='virtualserver',
            old_name='profile_1',
            new_name='profiles',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_2',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_3',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_4',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_5',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_6',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_7',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_8',
        ),
        migrations.RemoveField(
            model_name='virtualserver',
            name='profile_9',
        ),
    ]
