from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from ..helpers import addContext, getPBIfromProj

class HomeView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login'
    template_name = 'backtrack/home.html'

    def get_context_data(self, **kwargs):
        if self.request.user.projectParticipant.filter(project__complete=False).exists():
            # If user has a project that is not yet completed
            context = {}
            # Add context variables for sidebar
            context = addContext(self, context)
        else:
            context = {}
        return context
