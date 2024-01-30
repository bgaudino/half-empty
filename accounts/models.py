from django.db import models

from authtools.models import AbstractEmailUser

from core.models import TimeStampedModel


class User(AbstractEmailUser):
    def get_short_name(self):
        if hasattr(self, 'profile'):
            return self.profile.preferred_name or self.profile.name
        return super().get_short_name()

    def get_full_name(self):
        if hasattr(self, 'profile'):
            return self.profile.full_name
        return super().get_full_name()


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=255)
    preferred_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.full_name
