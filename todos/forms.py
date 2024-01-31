from django import forms

from . import models


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
            project_queryset = self.user.project_set.all()
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
    tag = forms.CharField(max_length=255, required=False, widget=forms.TextInput({'list': 'tags'}))
    deadline_start = forms.DateField(required=False, widget=forms.DateInput({'type': 'date', 'class': 'p-form__control'}))
    deadline_end = forms.DateField(required=False, widget=forms.DateInput({'type': 'date'}))
    completed = forms.BooleanField(required=False)
    in_trash = forms.BooleanField(required=False)
