# Generated by Django 4.1.3 on 2023-03-13 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0008_remove_feed_unique name and owner bond_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='date_created',
            field=models.DateTimeField(default='2023-03-13 17:56:26+00:00'),
        ),
    ]
