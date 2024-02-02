from django.contrib import admin

from . import models


@admin.register(models.ContactFormSubmission)
class ContactFormSubmission(admin.ModelAdmin):
    pass
