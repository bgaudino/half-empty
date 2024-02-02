from django.conf import settings
from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactFormSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)
    email = models.EmailField(blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=~models.Q(message='', user__isnull=True),
                name='user_or_email_required',
                violation_error_message='Please provide your email or log in',
            ),
        )

    def __str__(self):
        return f'{self.get_email()} - {self.created_at}'

    def get_absolute_url(self):
        return reverse('admin:core_contactformsubmission_change', args=(self.pk,))

    def get_email(self):
        return self.user.email if self.is_existing_user() else self.email

    def is_existing_user(self):
        return self.user is not None
