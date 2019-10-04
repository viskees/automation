# Generated by Django 2.2.4 on 2019-09-25 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0005_virtualserver'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificates',
            name='certificateKeySize',
            field=models.CharField(default='nogintevullen', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='city',
            field=models.CharField(default='çity', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='commonName',
            field=models.CharField(default='CN', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='organization',
            field=models.CharField(default='org', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='ou',
            field=models.CharField(default='ou', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='publicKeyType',
            field=models.CharField(default='pubkey type', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='state',
            field=models.CharField(default='state', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificates',
            name='subjectAlternativeName',
            field=models.CharField(default='san', max_length=2048),
            preserve_default=False,
        ),
    ]