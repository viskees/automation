# Generated by Django 2.2.4 on 2020-04-26 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualservers', '0002_auto_20200321_2148'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualServerVerzamel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vs_name', models.CharField(max_length=200)),
                ('vs_ip', models.CharField(max_length=200)),
                ('vs_cluster', models.CharField(max_length=200)),
                ('vs_irule', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['vs_cluster'],
            },
        ),
        migrations.DeleteModel(
            name='VirtualServerCluster',
        ),
    ]
