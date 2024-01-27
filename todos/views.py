from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from . import models


class TodoListView(LoginRequiredMixin, ListView):
    model = models.Todo
    context_object_name = 'todos'

    def get_queryset(self):
        return self.model.objects.all()
