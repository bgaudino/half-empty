from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, View

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
        context['add_tag_form'] = forms.AddTagForm()
        context['tags'] = self.request.user.tag_set.all()
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


class TodoDetailView(LoginRequiredMixin, DetailView):
    model = models.Todo
    context_object_name = 'todo'

    def get_queryset(self):
        return self.request.user.todo_set.all()


class TagFormView(LoginRequiredMixin, View):
    def post(self, request):
        form = forms.AddTagForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        tag, _ = models.Tag.objects.get_or_create(user=request.user, name=form.cleaned_data['tag'])
        tag_ids = request.POST.getlist('tags', [])
        if tag not in tag_ids:
            tag_ids.append(tag.pk)
        selected = models.Tag.objects.filter(user=request.user, pk__in=tag_ids)
        return render(request, 'todos/partials/_tag_form.html', {
            'tags': request.user.tag_set.all(),
            'selected': selected,
            'add_tag_form': forms.AddTagForm(),
        })
