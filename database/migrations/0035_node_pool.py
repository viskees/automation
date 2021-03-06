# Generated by Django 2.2.4 on 2020-04-26 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0034_irule_irule_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('partition', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=200)),
                ('monitor', models.CharField(max_length=200)),
                ('bigip_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.BigIPNodes')),
            ],
            options={
                'ordering': ['bigip_name'],
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('partition', models.CharField(max_length=200)),
                ('monitors', models.TextField()),
                ('bigip_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.BigIPNodes')),
                ('members', models.ManyToManyField(to='database.Node')),
            ],
            options={
                'ordering': ['bigip_name'],
            },
        ),
    ]
