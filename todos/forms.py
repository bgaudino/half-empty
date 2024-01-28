from django import forms

from . import models


class TodoForm(forms.ModelForm):
    class Meta:
        model = models.Todo
        fields = ('name', 'deadline', 'description')
        widgets = {
            'description': forms.Textarea({'rows': 3}),
            'deadline': forms.DateTimeInput({'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.user = self.user
        return super().save(commit)
