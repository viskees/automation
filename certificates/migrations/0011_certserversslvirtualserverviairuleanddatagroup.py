# Generated by Django 2.2.4 on 2020-02-10 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0010_certserversslvirtualserver'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertServerSSLVirtualServerViaIruleAndDatagroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cert_name', models.CharField(max_length=200)),
                ('cert_partition', models.CharField(max_length=200)),
                ('cert_expiration', models.DateTimeField()),
                ('cert_cluster', models.CharField(max_length=200)),
                ('server_ssl_name', models.CharField(max_length=200)),
                ('server_ssl_partition', models.CharField(max_length=200)),
                ('irule_name', models.CharField(max_length=200)),
                ('datagroup_name', models.CharField(max_length=200)),
                ('vs_name', models.CharField(max_length=200)),
                ('vs_partition', models.CharField(max_length=200)),
                ('vs_ip', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['cert_expiration'],
            },
        ),
    ]
