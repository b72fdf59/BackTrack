from ..models import Project
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.models import User

class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name']
    login_url = '/accounts/login'
    template_name = "backtrack/createProject.html"

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.instance.product_owner = self.request.user
        response = super().form_valid(form)
        print(self.request.user.profile)
        self.request.user.profile.project = self.object
        self.request.user.profile.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(profile__project_id__isnull = True)
        return context