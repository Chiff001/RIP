# Generated by Django 5.1.1 on 2024-10-20 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_alter_company_accepted_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalities',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
