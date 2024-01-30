from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel


class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    deadline = models.DateTimeField(null=True, blank=True)
    is_trashed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Todo(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_trashed = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('todo_detail', kwargs={'pk': self.pk})

    def toggle_completion(self):
        self.completed_at = None if self.is_completed else timezone.now()
        self.save()

    @property
    def is_completed(self):
        return self.completed_at is not None
