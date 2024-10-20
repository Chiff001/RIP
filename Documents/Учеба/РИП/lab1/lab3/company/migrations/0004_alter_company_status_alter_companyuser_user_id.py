# Generated by Django 5.1.1 on 2024-10-20 19:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_personalities_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='status',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='companyuser',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='company.personalities'),
        ),
    ]
