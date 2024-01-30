from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .middleware import HtmxMiddleware


class HtmxMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def process_response(self, request):
        HtmxMiddleware(lambda _: HttpResponse())(request)

    def test_is_htmx(self):
        request = self.factory.get(reverse('todo_list'))
        self.process_response(request)
        self.assertFalse(request.is_htmx)

    def test_is_not_htmx(self):
        request = self.factory.get(reverse('todo_list'))
        request.headers
        del request.headers
        request.headers = {'HX-Request': 'true'}
        self.process_response(request)
        self.assertTrue(request.is_htmx)
