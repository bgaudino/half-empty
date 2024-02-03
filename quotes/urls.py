from django.urls import path

from . import views

urlpatterns = [
    path('', views.QuoteView.as_view(), name='get_quote'),
    path('submit/', views.QuoteSubmissionView.as_view(), name='submit_quote'),
]
