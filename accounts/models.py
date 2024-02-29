from django.conf import settings
from django.db import models
from django.db.models.functions import Lower

from authtools.models import AbstractEmailUser

from core.models import TimeStampedModel
from todos.models import ORDERING


class User(AbstractEmailUser):
    def get_short_name(self):
        if hasattr(self, 'profile'):
            return self.profile.preferred_name or self.profile.name
        return super().get_short_name()

    def get_full_name(self):
        if hasattr(self, 'profile'):
            return self.profile.full_name
        return super().get_full_name()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            Settings.objects.create(user=self)


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=255)
    preferred_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.full_name


class Settings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    hide_completed_todos = models.BooleanField(default=False)
    receive_email_reminders = models.BooleanField(default=True)
    default_ordering = models.CharField(choices=ORDERING, max_length=11, default='created_at')

    def __str__(self):
        return f'Settings for {self.user}'

    def get_default_ordering(self):
        if self.default_ordering == 'name':
            return Lower(self.default_ordering)
        if self.default_ordering == '-name':
            return Lower('name').desc()
        return self.default_ordering
