# Generated by Django 3.0.7 on 2022-02-14 07:34

import django.core.files.storage
from django.db import migrations, models
import retina_grader.models


class Migration(migrations.Migration):

    dependencies = [
        ('retina_grader', '0002_auto_20220131_1220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='point',
            old_name='X',
            new_name='x',
        ),
        migrations.AddField(
            model_name='polygon',
            name='bone_number',
            field=models.CharField(blank=True, default='unknown', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='polygon',
            name='fracture_on_current_view',
            field=models.CharField(blank=True, default='No', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='polygon',
            name='fracture_on_other_view',
            field=models.CharField(blank=True, default='No', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='polygon',
            name='view_type',
            field=models.CharField(blank=True, default='unknown', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.ImageField(blank=True, height_field='height', null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/war454/even_more_images'), upload_to=retina_grader.models.get_file_location_path, width_field='width'),
        ),
    ]
