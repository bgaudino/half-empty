from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from . import models
from . import forms
from quotes.views import QuoteMixin


class TodoListView(LoginRequiredMixin, QuoteMixin, ListView):
    context_object_name = 'todos'
    paginate_by = 10

    def get_queryset(self):
        form = forms.FilterTodosForm(self.request.GET, user=self.request.user)
        form.full_clean()
        self.filters = form.cleaned_data
        qs = self.request.user.todo_set.order_by('created_at', 'name')
        if search := self.filters.get('search'):
            qs = qs.filter(name__icontains=search)
        if tag := self.filters.get('tag'):
            qs = qs.filter(tags__name=tag)
        match self.filters.get('status'):
            case 'completed':
                qs = qs.completed()
            case 'in_trash':
                qs = qs.trashed()
            case 'todo':
                qs = qs.todo()
            case 'overdue':
                qs = qs.overdue()
            case _:
                qs = qs.active()
        if project := self.filters.get('project'):
            qs = qs.filter(project=project)
        if deadline_start := self.filters.get('deadline_start'):
            qs = qs.filter(deadline__gte=deadline_start)
        if deadline_end := self.filters.get('deadline_end'):
            qs = qs.filter(deadline__lte=deadline_end)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.is_htmx:
            context['add_todo_form'] = forms.TodoForm(user=self.request.user)
            context['add_tag_form'] = forms.AddTagForm()
            tags = self.request.user.tag_set.all()
            context['tags'] = tags
            context['filter_todos_form'] = forms.FilterTodosForm(initial=self.request.GET)
        chips = []
        if search := self.filters.get('search'):
            chips.append(('Search', search))
        if tag := self.filters.get('tag'):
            chips.append(('Tag', tag))
        if status := self.filters.get('status'):
            chips.append(('Status', status.replace('_', ' ').title()))
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
        return self.request.user.todo_set.with_tags().order_by('created_at', 'name')

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

    def form_valid(self, form):
        todo = form.save()
        return HttpResponse(headers={'HX-Redirect': todo.get_absolute_url()})


class TodoCreateView(LoginRequiredMixin, View):
    form_class = forms.TodoForm
    template_name = 'todos/partials/_todo_li.html'

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
        return render(
            request, 'todos/partials/_completable.html',
            {'completable': todo, 'class_name': request.GET.get('class_name')}
        )


class TodoTrashView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(models.Todo, user=request.user, pk=pk)
        todo.is_trashed = True
        todo.save()
        return HttpResponse()


class TodoDetailView(LoginRequiredMixin, QuoteMixin, DetailView):
    model = models.Todo
    context_object_name = 'todo'

    def get_queryset(self):
        return self.request.user.todo_set.with_project().all()


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


class ProjectListView(LoginRequiredMixin, QuoteMixin, ListView):
    context_object_name = 'projects'

    def get_queryset(self):
        return self.request.user.project_set.active().with_todo_count().all()


class ProjectDetailView(LoginRequiredMixin, QuoteMixin, DetailView):
    context_object_name = 'project'

    def get_queryset(self):
        return self.request.user.project_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TodoForm(user=self.request.user, project=self.object)
        context['add_todo_form'] = form
        context['filter_todos_form'] = forms.FilterTodosForm(
            initial=self.request.GET,
            project=self.object,
        )
        context['todos'] = self.object.todo_set.active().order_by('created_at', 'name')
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = models.Project
    form_class = forms.ProjectForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context


class ProjectUpdateForm(LoginRequiredMixin, UpdateView):
    model = models.Project
    fields = ('name', 'description', 'deadline')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        return context


class ProjectTrashView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(models.Project, user=request.user, pk=pk)
        project.trash()
        return HttpResponse(headers={'HX-Redirect': reverse('project_list')})


class ProjectToggleCompletionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(models.Project, user=request.user, pk=pk)
        project.toggle_completion()
        return render(
            request, 'todos/partials/_completable.html',
            {'completable': project, 'class_name': request.GET.get('class_name')}
        )
