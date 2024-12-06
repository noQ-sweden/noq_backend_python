# Generated by Django 5.1.3 on 2024-11-19 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_host_caseworkers_alter_sleepingspace_bed_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='is_drugtolerant',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='host',
            name='max_days_per_booking',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='host',
            name='website',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]