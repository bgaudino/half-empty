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


class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_trashed=False)

    def todo(self):
        return self.active().filter(completed_at__isnull=True)

    def trashed(self):
        return self.filter(is_trashed=True)

    def completed(self):
        return self.filter(completed_at__isnull=False)

    def overdue(self):
        return self.filter(deadline__lt=timezone.now())


class AbstractTaskModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    deadline = models.DateTimeField(null=True, blank=True)
    is_trashed = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def is_completed(self):
        return self.completed_at is not None

    def toggle_completion(self):
        self.completed_at = None if self.is_completed else timezone.now()
        self.save()

    def trash(self):
        self.is_trashed = True
        self.save()


class ProjectQuerySet(TaskQuerySet):
    def with_todo_count(self):
        return self.annotate(todo_count=models.Count('todo', filter=models.Q(todo__is_trashed=False, todo__completed_at__isnull=True)))


class Project(TimeStampedModel, AbstractTaskModel):
    objects = ProjectQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

    def has_todos_remaining(self):
        return self.todo_set.active().todo().count() > 0

    def trash(self):
        super().trash()
        self.todo_set.update(is_trashed=True)


class TodoQuerySet(TaskQuerySet):
    def with_project(self):
        return self.select_related('project')

    def with_tags(self):
        return self.prefetch_related('tags').annotate(tag_count=models.Count('tags'))


class Todo(TimeStampedModel, AbstractTaskModel):
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = TodoQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('todo_detail', kwargs={'pk': self.pk})

    def convert_to_project(self):
        project = Project.objects.create(
            user=self.user,
            name=self.name,
            deadline=self.deadline,
        )
        self.delete()
        return project
