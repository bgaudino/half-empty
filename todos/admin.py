from django.contrib import admin

from . import models


@admin.register(models.Todo)
class TodoAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    pass
