# Generated by Django 2.2.4 on 2020-01-07 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0025_profilesslserver_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilesslserver',
            name='certificate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='database.Certificates'),
        ),
    ]
