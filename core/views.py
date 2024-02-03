from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from .forms import ContactForm
from .models import ContactFormSubmission


class MessageMixin(FormView):
    success_messages = ['Form successfully submitted']
    error_messages = ['Please correct the following errors']

    def add_success_messages(self):
        success_messages = self.success_messages
        if hasattr(self, 'get_success_messages'):
            success_messages = self.get_success_messages()
        if success_messages is not None:
            for message in success_messages:
                messages.add_message(self.request, messages.SUCCESS, message)

    def add_error_messages(self):
        error_messages = self.error_messages
        if hasattr(self, 'get_error_messages'):
            error_messages = self.get_error_messages()
        if error_messages is not None:
            for message in error_messages:
                messages.add_message(self.request, messages.ERROR, message)

    def form_invalid(self, form):
        res = super().form_invalid(form)
        self.add_error_messages()
        return res

    def form_valid(self, form):
        res = super().form_valid(form)
        self.add_success_messages()
        return res


class ContactFormView(MessageMixin, CreateView):
    model = ContactFormSubmission
    form_class = ContactForm
    success_url = reverse_lazy('index')
    success_messages = ['Your message is sent. Someone will get back to you soon!']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ContactFormSubmission.objects.filter(user=self.request.user)
        return ContactFormSubmission.objects.filter(user__isnull=True)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        return context

    def form_invalid(self, form):
        if errors := form.errors.get('g-recaptcha-response'):
            messages.add_message(self.request, messages.ERROR, 'reCaptcha: {}'.format('\n'.join(errors)))
        return super().form_invalid(form)
