# Generated by Django 4.2.9 on 2024-02-27 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0004_project_completed_at_project_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='priority',
            field=models.IntegerField(blank=True, choices=[(0, 'Urgent'), (1, 'High'), (2, 'Medium'), (3, 'Low')], max_length=4, null=True),
        ),
        migrations.AddConstraint(
            model_name='todo',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('priority__gte', 0), ('priority__lte', 3)), ('priority__isnull', True), _connector='OR'), name='priority_invalid_choice', violation_error_message='Invalid choice for priority'),
        ),
    ]
