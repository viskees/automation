# Generated by Django 2.2.4 on 2020-01-07 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0026_auto_20200107_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilesslserver',
            name='certificate',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='database.Certificates'),
            preserve_default=False,
        ),
    ]
