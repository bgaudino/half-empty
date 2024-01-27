from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, View

from . import models
from . import forms


class TodoListView(LoginRequiredMixin, ListView):
    model = models.Todo
    context_object_name = 'todos'

    def get_queryset(self):
        return self.model.objects.filter(is_trashed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_todo_form'] = forms.TodoForm()
        return context


class TodoCreateView(LoginRequiredMixin, View):
    form_class = forms.TodoForm
    template_name = 'todos/partials/_todo.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user=self.request.user)
        if form.is_valid():
            todo = form.save()
        else:
            raise HttpResponseBadRequest()
        return render(request, self.template_name, {'todo': todo})


class TodoToggleCompletionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(models.Todo, user=request.user, pk=pk)
        todo.toggle_completion()
        return render(request, 'todos/partials/_todo.html', {'todo': todo})


class TodoTrashView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(models.Todo, user=request.user, pk=pk)
        todo.is_trashed = True
        todo.save()
        return HttpResponse()
