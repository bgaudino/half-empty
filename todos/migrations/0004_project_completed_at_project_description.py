# Generated by Django 4.2.9 on 2024-01-31 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0003_project_created_at_project_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
