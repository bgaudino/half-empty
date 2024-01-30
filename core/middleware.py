class HtmxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, 'is_htmx', request.headers.get('HX-Request') == 'true')
        response = self.get_response(request)
        return response
