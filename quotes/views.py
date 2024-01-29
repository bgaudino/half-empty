from django.views.generic import TemplateView

from . import models


class QuoteView(TemplateView):
    template_name = 'quotes/partials/_quote.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = models.Quote.objects
        if previous := self.request.GET.get('previous'):
            qs = qs.exclude(pk=previous)
        context['quote'] = qs.first()
        return context
