from django.urls import include, path

from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile_create'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
]
