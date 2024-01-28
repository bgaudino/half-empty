from django import forms

from . import models


class TodoForm(forms.ModelForm):
    class Meta:
        model = models.Todo
        fields = ('name', 'deadline', 'description', 'tags')
        labels = {
            'name': 'New todo'
        }
        widgets = {
            'name': forms.TextInput({'autoFocus': True}),
            'description': forms.Textarea({'rows': 3}),
            'deadline': forms.DateTimeInput({'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['tags'].queryset = self.user.tag_set.all()

    def save(self, commit=True):
        self.instance.user = self.user
        return super().save(commit)


class AddTagForm(forms.Form):
    tag = forms.CharField(max_length=255, label='Tags', widget=forms.TextInput({'list': 'tags'}))
