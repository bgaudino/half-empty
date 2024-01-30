from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('quotes/', include('quotes.urls')),
    path('', include('todos.urls')),
]


if settings.DEBUG:
    try:
        urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')),)
    except ImportError:
        pass
