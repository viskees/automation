# Generated by Django 2.2.4 on 2020-01-02 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0020_auto_20200102_1552'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='certificates',
            options={'ordering': ['bigip_name']},
        ),
        migrations.AlterModelOptions(
            name='profilesslclient',
            options={'ordering': ['bigip_name']},
        ),
        migrations.AlterModelOptions(
            name='profilesslserver',
            options={'ordering': ['bigip_name']},
        ),
        migrations.AlterModelOptions(
            name='virtualserver',
            options={'ordering': ['bigip_name']},
        ),
        migrations.AddField(
            model_name='certificates',
            name='profile_ssl_client',
            field=models.ManyToManyField(to='database.ProfileSSLClient'),
        ),
        migrations.AddField(
            model_name='certificates',
            name='profile_ssl_server',
            field=models.ManyToManyField(to='database.ProfileSSLServer'),
        ),
        migrations.AddField(
            model_name='profilesslclient',
            name='virtual_server',
            field=models.ManyToManyField(to='database.VirtualServer'),
        ),
        migrations.AddField(
            model_name='profilesslserver',
            name='virtual_server',
            field=models.ManyToManyField(to='database.VirtualServer'),
        ),
        migrations.DeleteModel(
            name='KoppelCSSLCert',
        ),
    ]
