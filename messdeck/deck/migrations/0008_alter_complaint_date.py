# Generated by Django 4.2.5 on 2023-11-24 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0007_complaint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
