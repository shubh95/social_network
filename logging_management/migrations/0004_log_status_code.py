# Generated by Django 5.1.1 on 2024-10-02 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logging_management', '0003_alter_log_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='status_code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
