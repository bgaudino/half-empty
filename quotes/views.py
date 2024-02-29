from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .models import Quote
from .forms import QuoteForm
from core.views import FormMessageView


class QuoteView(TemplateView):
    template_name = 'quotes/partials/_quote.html'


class QuoteSubmissionView(FormMessageView, CreateView):
    model = Quote
    form_class = QuoteForm
    success_messages = ['Quote successfully submitted']
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        return super().form_invalid(form)
