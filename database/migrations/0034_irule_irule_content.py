# Generated by Django 2.2.4 on 2020-02-28 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0033_auto_20200208_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='irule',
            name='irule_content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]