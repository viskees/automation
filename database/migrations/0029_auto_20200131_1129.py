# Generated by Django 2.2.4 on 2020-01-31 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0028_auto_20200107_1634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificates',
            name='profile_ssl_client',
        ),
        migrations.RemoveField(
            model_name='profilesslclient',
            name='virtual_server',
        ),
        migrations.RemoveField(
            model_name='profilesslserver',
            name='virtual_server',
        ),
        migrations.AddField(
            model_name='profilesslclient',
            name='certificates',
            field=models.ManyToManyField(to='database.Certificates'),
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='profile_client_ssl',
            field=models.ManyToManyField(to='database.ProfileSSLClient'),
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='profile_server_ssl',
            field=models.ManyToManyField(to='database.ProfileSSLServer'),
        ),
    ]
