# Generated by Django 3.0.7 on 2024-02-01 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retina_grader', '0010_auto_20240201_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rectangle',
            name='osteomyelitis_present_score',
            field=models.FloatField(default=0.0),
        ),
    ]