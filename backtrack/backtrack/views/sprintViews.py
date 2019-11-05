from django.views.generic import CreateView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from ..models import Sprint, Project
from ..forms import CreateSprintForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.models import User


class CreateSprint(LoginRequiredMixin, CreateView):
    model = Sprint
    form_class = CreateSprintForm
    template_name = "backtrack/createSprint.html"
    login_url = '/accounts/login'

    # def get_success_url(self):
    #     return reverse("detail-sprint", kwargs={"pk": self.instance.project.id, "spk": self.instance.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(
            projectParticipant__isnull=True).exclude(username=self.request.user.username)
        context['projectID'] = self.kwargs['pk']
        context['Project'] = self.request.user.projectParticipant.get(
            project__complete=False).project
        context['ProjectParticipant'] = self.request.user.projectParticipant.get(
            project__complete=False)
        context['Sprints'] = self.request.user.projectParticipant.get(
            project__complete=False).project.sprint.all()
        return context

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        sprintList = project.sprint.all()
        print(sprintList)
        for sprint in sprintList:
            print(sprint.available)
            if sprint.available:
                raise Exception("Sprint is already in Progress")
        form.instance.project = project
        return super().form_valid(form)


class SprintDetail(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login'
    template_name = 'backtrack/sprintDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(
            projectParticipant__isnull=True).exclude(username=self.request.user.username)
        context['projectID'] = self.kwargs['pk']
        context['Project'] = self.request.user.projectParticipant.get(
            project__complete=False).project
        context['ProjectParticipant'] = self.request.user.projectParticipant.get(
            project__complete=False)
        context['Sprints'] = self.request.user.projectParticipant.get(
            project__complete=False).project.sprint.all()
        return context
