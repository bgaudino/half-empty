from django.contrib import admin

from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile


class SettingsInline(admin.StackedInline):
    model = models.Settings


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline, SettingsInline)
