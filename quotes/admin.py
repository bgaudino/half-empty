from django.contrib import admin

from . import models


@admin.register(models.Quote)
class QuoteAdmin(admin.ModelAdmin):
    pass
