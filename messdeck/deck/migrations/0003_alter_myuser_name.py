# Generated by Django 4.2.5 on 2023-11-22 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0002_myuser_bits_id_myuser_hostel_myuser_mess_myuser_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='Name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]