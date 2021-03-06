# Generated by Django 2.2.4 on 2019-09-11 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0004_auto_20190907_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('partition', models.CharField(max_length=200)),
                ('destination', models.CharField(max_length=200)),
                ('bigip_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.BigIPNodes')),
                ('profilesslclient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.ProfileSSLClient')),
            ],
        ),
    ]
