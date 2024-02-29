from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, FormView, TemplateView

from . import models
from . import forms
from core.views import FormMessageView


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


class ProfileCreateView(LoginRequiredMixin, FormMessageView, CreateView):
    model = models.Profile
    fields = ('full_name', 'preferred_name')
    success_url = reverse_lazy('profile_detail')
    success_messages = ['Profile successfully created']

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


class ProfileUpdateView(LoginRequiredMixin, NoProfileMixin, FormMessageView, UpdateView):
    model = models.Profile
    fields = ('full_name', 'preferred_name')
    success_url = reverse_lazy('profile_detail')
    success_messages = ['Profile successfully updated']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        return context


class SignupView(FormMessageView, FormView):
    form_class = forms.SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy(('profile_detail'))
    success_messages = ['Your account was successfully created. Take a minute to fill out your profile']

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.add_success_messages()
        return super().form_valid(form)


class SecurityView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/security.html'


class PasswordChangeView(LoginRequiredMixin, FormMessageView, auth_views.PasswordChangeView):
    success_url = reverse_lazy('security')
    success_messages = ['Your password was successfully changed']


class SettingsView(LoginRequiredMixin, FormMessageView, UpdateView):
    success_messages = ['Your preferences have been successfully updated']
    success_url = reverse_lazy('settings')
    fields = ('hide_completed_todos', 'default_ordering')

    def get_object(self, *args, **kwargs):
        return self.request.user.settings
