from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.forms.renderers import TemplatesSetting

import requests

from . import models


class VanillaFormRenderer(TemplatesSetting):
    form_template_name = 'core/forms/form.html'


def google_captcha_validator(value):
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': value,
        }
    )

    if not response.json().get('success'):
        raise forms.ValidationError('Invalid reCAPTCHA')


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.ContactFormSubmission
        fields = ('email', 'message')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields.pop('email')
        else:
            self.fields['email'].required = True
            self.fields['g-recaptcha-response'] = forms.fields.CharField(
                widget=forms.HiddenInput,
                validators=[google_captcha_validator],
                required=True,
            )

    def save(self, commit=True):
        is_new = self.instance.pk is None
        if self.user:
            self.instance.user = self.user
        instance = super().save(commit)
        if is_new:
            send_mail(
                'Contact form submitted',
                'New contact form submission.',
                settings.CONTACT_EMAIL,
                (settings.CONTACT_EMAIL,),
                html_message=f'''View it <a href="{settings.SITE_URL}{instance.get_absolute_url()}">here</a>'''
            )
        return instance
