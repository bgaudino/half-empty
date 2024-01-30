from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, FormView, TemplateView

from . import models
from . import forms


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


class SignupView(FormView):
    form_class = forms.SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy(('profile_detail'))

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.add_message(self.request, messages.SUCCESS, 'Your account was successfully created. Take a minute to fill out your profile')
        return super().form_valid(form)


class SecurityView(TemplateView):
    template_name = 'registration/security.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('security')

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Your password was changed')
        return super().form_valid(form)
