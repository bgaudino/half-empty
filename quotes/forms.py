from django import forms
from django.conf import settings
from django.core.mail import send_mail

from .models import Quote
from core.forms import RecaptchaForm


class QuoteForm(RecaptchaForm, forms.ModelForm):
    class Meta:
        model = Quote
        fields = ('submitted_by_email', 'text', 'attributed_to')
        labels = {
            'submitted_by_email': 'Email',
            'text': 'Quote',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields.pop('submitted_by_email')
            self.fields.pop('g-recaptcha-response')

    def save(self, commit=True):
        is_new = self.instance.pk is None
        if self.user:
            self.instance.submitted_by_user = self.user
        instance = super().save(commit)
        if is_new:
            send_mail(
                'Quote Submission',
                'Someone submitted a quote.',
                settings.CONTACT_EMAIL,
                (settings.CONTACT_EMAIL,),
                html_message=f'''View it <a href="{settings.SITE_URL}{instance.get_absolute_url()}">here</a>'''
            )
        return instance
