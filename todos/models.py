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


class AbstractTaskModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    deadline = models.DateTimeField(null=True, blank=True)
    is_trashed = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def toggle_completion(self):
        self.completed_at = None if self.is_completed else timezone.now()
        self.save()


class Project(TimeStampedModel, AbstractTaskModel):
    pass

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

    def has_todos_remaining(self):
        return self.todo_set.active().todo().count() > 0


class TodoQuerySet(models.QuerySet):
    def with_project(self):
        return self.select_related('project')

    def with_tags(self):
        return self.prefetch_related('tags')

    def active(self):
        return self.filter(is_trashed=False)

    def trashed(self):
        return self.filter(is_trashed=True)

    def todo(self):
        return self.filter(completed_at__isnull=True)

    def completed(self):
        return self.filter(completed_at__isnull=False)

    def overdue(self):
        return self.filter(deadline__lt=timezone.now())


class Todo(TimeStampedModel, AbstractTaskModel):
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = TodoQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('todo_detail', kwargs={'pk': self.pk})

    @property
    def is_completed(self):
        return self.completed_at is not None

    def convert_to_project(self):
        project = Project.objects.create(
            user=self.user,
            name=self.name,
            deadline=self.deadline,
        )
        self.delete()
        return project
