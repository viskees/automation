# Generated by Django 2.2.4 on 2020-01-02 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0019_auto_20200102_1506'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilesslclient',
            name='certificate',
        ),
        migrations.RemoveField(
            model_name='profilesslclient',
            name='virtual_server',
        ),
        migrations.RemoveField(
            model_name='profilesslserver',
            name='certificate',
        ),
        migrations.RemoveField(
            model_name='profilesslserver',
            name='virtual_server',
        ),
        migrations.CreateModel(
            name='KoppelCSSLCert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate', models.ManyToManyField(to='database.Certificates')),
                ('profile_ssl_client', models.ManyToManyField(to='database.ProfileSSLClient')),
            ],
        ),
    ]