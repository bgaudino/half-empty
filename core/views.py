from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ContactForm
from .models import ContactFormSubmission


class ContactFormView(CreateView):
    model = ContactFormSubmission
    form_class = ContactForm
    success_url = reverse_lazy('index')

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

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, 'Your message is sent. Someone will get back to you soon!')
        return res
