from django.views.generic import TemplateView


class QuoteView(TemplateView):
    template_name = 'quotes/partials/_quote.html'
