from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Project, ProjectParticipant
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render


class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name']
    login_url = '/accounts/login'
    template_name = "backtrack/createProject.html"

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        projectParticipant = ProjectParticipant(
            user=self.request.user, role="PO", project=form.instance)
        projectParticipant.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(projectParticipant__isnull=True).exclude(username=self.request.user.username)
        return context
