from django.db import models


class Quote(models.Model):
    text = models.TextField()
    attributed_to = models.CharField(max_length=255)

    def __str__(self):
        return f'Quote {self.pk}: {self.attributed_to}'

    class Meta:
        ordering = ('?',)
