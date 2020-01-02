# Generated by Django 2.2.4 on 2019-12-14 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0014_auto_20191213_1411'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileSSLServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('partition', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('bigip_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.BigIPNodes')),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Certificates')),
            ],
        ),
    ]