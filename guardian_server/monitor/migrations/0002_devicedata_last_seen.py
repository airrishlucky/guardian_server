# Generated by Django 5.2.3 on 2025-06-14 07:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicedata',
            name='last_seen',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
