# Generated by Django 4.2.5 on 2023-11-22 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='BITS_ID',
            field=models.CharField(max_length=14, null=True),
        ),
        migrations.AddField(
            model_name='myuser',
            name='Hostel',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='myuser',
            name='Mess',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='myuser',
            name='Name',
            field=models.CharField(default='Ghot', max_length=50),
        ),
        migrations.AddField(
            model_name='myuser',
            name='PSRN_No',
            field=models.BigIntegerField(null=True),
        ),
    ]