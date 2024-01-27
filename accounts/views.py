from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView

from . import models


class NoProfileMixin:
    def dispatch(self, request, *args, **kwargs):
        if getattr(self.request.user, 'profile', None) is None:
            return redirect(reverse('profile_create'))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileDetailView(LoginRequiredMixin, NoProfileMixin, DetailView):
    model = models.Profile
    context_object_name = 'profile'


class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = models.Profile
    fields = ('full_name', 'preferred_name')
    success_url = reverse_lazy('profile_detail')

    def dispatch(self, request, *args, **kwargs):
        if getattr(self.request.user, 'profile', None) is not None:
            return redirect(reverse('profile_detail'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, NoProfileMixin, UpdateView):
    model = models.Profile
    fields = ('full_name', 'preferred_name')
    success_url = reverse_lazy('profile_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        return context
