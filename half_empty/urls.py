from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('quotes/', include('quotes.urls')),
    path('', include('todos.urls')),
]
