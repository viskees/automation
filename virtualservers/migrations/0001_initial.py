# Generated by Django 2.2.4 on 2020-03-21 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vs_name', models.CharField(max_length=200)),
                ('vs_ip', models.CharField(max_length=200)),
                ('vs_cluster', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['vs_cluster'],
            },
        ),
    ]
