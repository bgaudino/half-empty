# Generated by Django 4.2.9 on 2024-02-29 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0005_todo_priority_todo_priority_invalid_choice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='priority',
            field=models.IntegerField(blank=True, choices=[(0, 'Urgent'), (1, 'High'), (2, 'Medium'), (3, 'Low')], null=True),
        ),
    ]
