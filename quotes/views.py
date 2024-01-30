from django.urls import reverse
from django.views.generic import TemplateView

from . import models


class QuoteMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.is_htmx or self.request.path == reverse('get_quote'):
            qs = models.Quote.objects
            if previous := self.request.GET.get('previous'):
                qs = qs.exclude(pk=previous)
            context['quote'] = qs.first()
        return context


class QuoteView(QuoteMixin, TemplateView):
    template_name = 'quotes/partials/_quote.html'
