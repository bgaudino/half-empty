from urllib.parse import urlparse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import resolve, reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from . import models
from . import forms
from core.paginator import GracefulPaginator
from core.views import FormMessageView


class FilterTodosMixin:
    def filter_todos(self, qs):
        form = forms.FilterTodosForm(data=self.request.GET, user=self.request.user)
        form.full_clean()
        self.filters = form.cleaned_data
        sort_form = forms.SortForm(self.request.GET, user=self.request.user)
        sort_form.full_clean()
        self.filters.update(sort_form.cleaned_data)
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
            case 'active':
                qs = qs.active()
            case _:
                if self.request.user.settings.hide_completed_todos:
                    qs = qs.todo()
                else:
                    qs = qs.active()
        if project := self.filters.get('project'):
            qs = qs.filter(project=project)
        if deadline_start := self.filters.get('deadline_start'):
            qs = qs.filter(deadline__gte=deadline_start)
        if deadline_end := self.filters.get('deadline_end'):
            qs = qs.filter(deadline__lte=deadline_end)
        if (priority := self.filters.get('priority')) is not None:
            qs = qs.filter(priority=priority)
        sort = self.filters.get('sort') or self.request.user.settings.get_default_ordering()
        qs = qs.order_by(sort, 'pk')
        return qs

    def get_chips(self):
        chips = []
        if search := self.filters.get('search'):
            chips.append(('Search', search))
        if tag := self.filters.get('tag'):
            chips.append(('Tag', tag))
        if status := self.filters.get('status'):
            chips.append(('Status', status.replace('_', ' ').title()))
        else:
            status = 'To do' if self.request.user.settings.hide_completed_todos else 'Active'
            chips.append(('Status', status))
        if (priority := self.filters.get('priority')) is not None:
            priority = next(p[1] for p in models.PRIORITIES if p[0] == priority)
            if priority:
                chips.append(('Priority', priority))
        start = self.filters.get('deadline_start')
        end = self.filters.get('deadline_end')
        if start and end:
            chips.append(('Deadline', f'{start} - {end}'))
        elif start:
            chips.append(('Deadline', f'{start} and later'))
        elif end:
            chips.append(('Deadline', f'{end} and earlier'))
        return chips


class TodoListView(LoginRequiredMixin, FilterTodosMixin, ListView):
    context_object_name = 'todos'
    paginate_by = 10
    paginator_class = GracefulPaginator

    def get_queryset(self):
        return self.filter_todos(self.request.user.todo_set.with_tags())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.is_htmx:
            context['add_todo_form'] = forms.TodoForm(user=self.request.user)
            context['add_tag_form'] = forms.AddTagForm()
            tags = self.request.user.tag_set.all()
            context['tags'] = tags
            context['filter_todos_form'] = forms.FilterTodosForm(
                initial=self.request.GET,
                user=self.request.user
            )
            context['sort_todos_form'] = forms.SortForm(
                initial=self.request.GET,
                user=self.request.user,
            )
        context['chips'] = self.get_chips()

        return context

    def get_template_names(self):
        if self.request.is_htmx:
            return ('todos/partials/_todo_list.html')
        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        headers = {}
        if referer := self.request.META.get('HTTP_REFERER'):
            _, _, path, *_ = urlparse(referer)
            url = '?'.join((path, self.request.GET.urlencode()))
            headers['Hx-Push-Url'] = url
        return super().render_to_response(context, headers=headers, **response_kwargs)


class TodoUpdateView(LoginRequiredMixin, FormMessageView, UpdateView):
    form_class = forms.TodoForm
    success_messages = ['Todo successfully updated']

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

    def form_invalid(self, form):
        res = super().form_invalid(form)
        res['HX-Retarget'] = 'body'
        return res

    def form_valid(self, form):
        todo = form.save()
        self.add_success_messages()
        return HttpResponse(headers={'HX-Redirect': todo.get_absolute_url()})


class TodoCreateView(LoginRequiredMixin, View):
    form_class = forms.TodoForm
    template_name = 'todos/partials/_todo_li.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user=self.request.user)
        if form.is_valid():
            form.save()
        else:
            return HttpResponseBadRequest()
        return HttpResponse(headers={'HX-Trigger': 'refetchTodos'})


class TodoToggleCompletionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(models.Todo, user=request.user, pk=pk)
        todo.toggle_completion()
        if referer := self.request.META.get('HTTP_REFERER'):
            _, _, path, *_ = urlparse(referer)
            if resolve(path).url_name == 'todo_detail':
                return render(
                    request,
                    'todos/partials/_completable.html',
                    {'completable': todo, 'is_detail': True, 'class_name': 'p-checkbox--heading'}
                )
        return HttpResponse(headers={'HX-Trigger': 'refetchTodos'})


class TodoTrashView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(models.Todo, user=request.user, pk=pk)
        todo.trash()
        return HttpResponse(headers={'HX-Trigger': 'refetchTodos'})


class TodoRestoreView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(request.user.todo_set.trashed(), pk=pk)
        todo.restore()
        return HttpResponse(headers={'HX-Trigger': 'refetchTodos'})


class TodoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(request.user.todo_set.trashed(), pk=pk)
        todo.delete()
        return HttpResponse(headers={'HX-Trigger': 'refetchTodos'})


class TodoDetailView(LoginRequiredMixin, DetailView):
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


class ConvertToProjectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(models.Todo, user=request.user, pk=pk)
        project = todo.convert_to_project()
        return HttpResponse(
            headers={
                'HX-Redirect': reverse('project_detail', kwargs={'pk': project.pk})
            }
        )


class ProjectListView(LoginRequiredMixin, ListView):
    context_object_name = 'projects'

    def get_queryset(self):
        return self.request.user.project_set.active().with_todo_count().all()


class ProjectDetailView(LoginRequiredMixin, FilterTodosMixin, DetailView):
    context_object_name = 'project'

    def get_queryset(self):
        return self.request.user.project_set.prefetch_related(
            Prefetch('todo_set', queryset=models.Todo.objects.active().with_tags())
        ).order_by('-created_at', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TodoForm(user=self.request.user, project=self.object)
        context['add_todo_form'] = form
        context['filter_todos_form'] = forms.FilterTodosForm(
            initial=self.request.GET,
            project=self.object,
            user=self.request.user,
        )
        qs = self.filter_todos(self.object.todo_set.with_tags())
        paginator = GracefulPaginator(qs, 10)
        page = paginator.get_page(self.request.GET.get('page', 1))
        context['page_obj'] = page
        context['todos'] = page.object_list
        context['sort_todos_form'] = forms.SortForm(
            initial=self.request.GET,
            user=self.request.user,
        )
        context['chips'] = self.get_chips()
        return context


class ProjectCreateView(LoginRequiredMixin, FormMessageView, CreateView):
    model = models.Project
    form_class = forms.ProjectForm
    success_messages = ['Project successfully created']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context


class ProjectUpdateForm(LoginRequiredMixin, FormMessageView, UpdateView):
    model = models.Project
    fields = ('name', 'description', 'deadline')
    success_messages = ['Project successfully updated']

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
            {'completable': project, 'class_name': request.GET.get('class_name'), 'is_detail': True}
        )
