from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import BaseModelForm
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, UpdateView, View

from . import models
from . import forms


class HtmxMixin(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        setattr(self.request, 'is_htmx', self.request.headers.get('HX-Request') == 'true')


class TodoListView(LoginRequiredMixin, HtmxMixin, ListView):
    context_object_name = 'todos'

    def get_queryset(self):
        form = forms.FilterTodosForm(self.request.GET)
        form.full_clean()
        self.filters = form.cleaned_data
        qs = self.request.user.todo_set.filter(is_trashed=self.filters.get('in_trash'))
        if tag := self.filters.get('tag'):
            qs = qs.filter(tags__name=tag)
        if self.filters.get('completed'):
            qs = qs.filter(completed_at__isnull=False)
        if deadline_start := self.filters.get('deadline_start'):
            qs = qs.filter(deadline__gte=deadline_start)
        if deadline_end := self.filters.get('deadline_end'):
            qs = qs.filter(deadline__lte=deadline_end)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.is_htmx:
            context['add_todo_form'] = forms.TodoForm()
            context['add_tag_form'] = forms.AddTagForm()
            tags = self.request.user.tag_set.all()
            context['tags'] = tags
            context['filter_todos_form'] = forms.FilterTodosForm(initial=self.request.GET)
        chips = []
        if tag := self.filters.get('tag'):
            chips.append(('Tag', tag))
        if self.filters.get('completed'):
            chips.append((None, 'Completed'))
        if self.filters.get('in_trash'):
            chips.append((None, 'In Trash'))
        start = self.filters.get('deadline_start')
        end = self.filters.get('deadline_end')
        if start and end:
            chips.append(('Deadline', f'{start} - {end}'))
        elif start:
            chips.append(('Deadline', f'{start} and later'))
        elif end:
            chips.append(('Deadline', f'{end} and earlier'))
        context['chips'] = chips
        return context

    def get_template_names(self):
        if self.request.is_htmx:
            return ('todos/partials/_todo_list.html')
        return super().get_template_names()


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    form_class = forms.TodoForm

    def get_queryset(self):
        return self.request.user.todo_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_tag_form'] = forms.AddTagForm()
        context['tags'] = self.request.user.tag_set.all()
        context['selected'] = self.object.tags.all()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form: BaseModelForm):
        todo = form.save()
        return HttpResponse(headers={'HX-Redirect': todo.get_absolute_url()})


class TodoCreateView(LoginRequiredMixin, HtmxMixin, View):
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


class TagAddView(LoginRequiredMixin, View):
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


class TagRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tag_ids = request.POST.getlist('tags', [])
        selected = models.Tag.objects.filter(user=request.user, pk__in=tag_ids).exclude(pk=pk)
        return render(request, 'todos/partials/_tag_form.html', {
            'tags': request.user.tag_set.all(),
            'selected': selected,
            'add_tag_form': forms.AddTagForm(initial=request.POST),
        })
