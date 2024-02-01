from django.test import TestCase
from django.urls import reverse

from .models import Quote


class QuoteViewTestCase(TestCase):
    def test_random_quote_excludes_previous(self):
        quote = Quote.objects.random()
        for _ in range(10):
            res = self.client.get(reverse('get_quote'), QUERY_STRING=f'previous={quote.pk}')
            new_quote = res.context['QUOTE']
            self.assertNotEqual(new_quote, quote)
            quote = new_quote
