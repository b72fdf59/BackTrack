from django.views.generic import CreateView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from ..models import Sprint, Project
from ..forms import CreateSprintForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.models import User
from ..helpers import addContext
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.contrib import messages


class CreateSprint(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sprint
    form_class = CreateSprintForm
    template_name = "backtrack/createSprint.html"
    login_url = '/accounts/login'
    success_message = "Sprint was created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = addContext(self, context)
        return context

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        sprintList = project.sprint.all()
        for sprint in sprintList:
            if sprint.available:
                messages.error(self.request,'Sprint is in Progress')
                return redirect(self.request.path_info)
        form.instance.project = project
        return super().form_valid(form)


class SprintDetail(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login'
    template_name = 'backtrack/sprintDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = addContext(self, context)
        return context
