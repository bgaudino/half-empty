from django.db import models


class QuoteQuerySet(models.QuerySet):
    def random(self):
        return self.order_by('?').first()


class Quote(models.Model):
    text = models.TextField()
    attributed_to = models.CharField(max_length=255)

    objects = QuoteQuerySet.as_manager()

    def __str__(self):
        return f'Quote {self.pk}: {self.attributed_to}'
