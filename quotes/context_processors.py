from .models import Quote


def quote(request):
    qs = Quote.objects
    if previous := request.GET.get('previous'):
        qs = qs.exclude(pk=previous)
    return {'QUOTE': qs.random()}
