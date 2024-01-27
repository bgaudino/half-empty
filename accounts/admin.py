from django.contrib import admin

from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
