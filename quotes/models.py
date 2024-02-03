from django.conf import settings
from django.db import models
from django.urls import reverse


class QuoteQuerySet(models.QuerySet):
    def accepted(self):
        return self.filter(is_accepted=True)

    def random(self):
        return self.accepted().order_by('?').first()


class Quote(models.Model):
    text = models.TextField(unique=True)
    attributed_to = models.CharField(max_length=255)
    is_accepted = models.BooleanField(default=False)
    submitted_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    submitted_by_email = models.EmailField(blank=True)

    objects = QuoteQuerySet.as_manager()

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=~models.Q(submitted_by_user__isnull=True, submitted_by_email=''),
                name='quote_user_or_email_required',
                violation_error_message='Please provide an email or login'
            ),
        )

    def __str__(self):
        return f'Quote {self.pk}: {self.attributed_to}'

    def get_absolute_url(self):
        return reverse('admin:quotes_quote_change', args=(self.pk,))

    def submitted_by(self):
        return self.submitted_by_user or self.submitted_by_email
