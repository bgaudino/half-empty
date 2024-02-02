from django import forms
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower

from . import models

User = get_user_model()


class TodoForm(forms.ModelForm):
    class Meta:
        model = models.Todo
        fields = ('name', 'project', 'deadline', 'description', 'tags')
        widgets = {
            'name': forms.TextInput({
                'placeholder': 'Add something to do',
                'autoFocus': True,
                'ariaLabel': 'Todo name',
            }),
            'description': forms.Textarea({'rows': 3}),
            'deadline': forms.DateTimeInput({'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        tag_queryset = models.Tag.objects.none()
        project_queryset = models.Project.objects.none()
        if self.user:
            tag_queryset = self.user.tag_set.all()
            project_queryset = self.user.project_set.todo().all()
        self.fields['tags'].queryset = tag_queryset
        self.fields['project'].queryset = project_queryset

        if self.project:
            self.fields['project'].widget = forms.HiddenInput()
            self.fields['project'].initial = self.project
            self.fields['project'].queryset = models.Project.objects.filter(pk=self.project.pk)

    def save(self, commit=True):
        self.instance.user = self.user
        return super().save(commit)


class AddTagForm(forms.Form):
    tag = forms.CharField(max_length=255, label='Tags', widget=forms.TextInput({'list': 'tags'}))


class FilterTodosForm(forms.Form):
    search = forms.CharField(max_length=255, required=False)
    tag = forms.CharField(max_length=255, required=False, widget=forms.TextInput({'list': 'tags'}))
    deadline_start = forms.DateField(required=False, widget=forms.DateInput({'type': 'date', 'class': 'p-form__control'}))
    deadline_end = forms.DateField(required=False, widget=forms.DateInput({'type': 'date'}))
    status = forms.ChoiceField(choices=(
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('todo', 'To do'),
        ('in_trash', 'In Trash'),
        ('overdue', 'Overdue'),
    ))
    project = forms.ModelChoiceField(
        models.Project.objects.none(),
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project:
            self.fields['project'].queryset = models.Project.objects.filter(pk=self.project.pk)
            self.fields['project'].initial = self.project
        elif self.user:
            self.fields['project'].queryset = self.user.project_set.all()


class SortForm(forms.Form):
    sort = forms.ChoiceField(choices=(
        ('created_at', 'Oldest'),
        ('-created_at', 'Newest'),
        ('name', 'A to Z'),
        ('-name', 'Z to A'),
        ('deadline', 'Deadline (earliest)'),
        ('-deadline', 'Deadline (latest)'),
    ))

    def clean_sort(self):
        sort = self.cleaned_data.get('sort')
        if sort == 'name':
            return Lower(sort)
        if sort == '-name':
            return Lower('name').desc()
        return sort


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('user', 'name', 'description', 'deadline')
        widgets = {
            'deadline': forms.DateTimeInput({'type': 'datetime-local'}),
            'user': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['user'].initial = user
        qs = User.objects
        qs = qs.filter(pk=user.pk) if user else qs.none()
