from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Project, ProjectParticipant
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from ..helpers import addContext

class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name']
    login_url = '/accounts/login'
    template_name = "backtrack/createProject.html"
    # success_url=reverse('create-project-developer',kwargs={'pk':self.object.id})

    def get_success_url(self):
        return reverse('invite-project-members', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        projectParticipant = ProjectParticipant(
            user=self.request.user, role="PO", project=form.instance)
        projectParticipant.save()
        return response


class InviteMember(LoginRequiredMixin, TemplateView):
    template_name = "backtrack/inviteDevelopers.html"
    login_url = '/accounts/login'

    def get_context_data(self, **kwargs):
        context = {}
        context['users'] = User.objects.filter(
        projectParticipant__isnull=True).exclude(username=self.request.user.username)
        context = addContext(self,context)
        print(context)
        return context


class EmailMember(LoginRequiredMixin, View):
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        userID = self.request.GET['id']
        recipient_email = get_object_or_404(User, id=userID).email
        username = self.request.user.username
        name = User.objects.get(id=userID).username
        fullPath = self.request.build_absolute_uri(
            reverse('add-project-developer', kwargs={'pk': kwargs['pk']}))
        link = "{}?id={}".format(
            fullPath, userID)
        subject = "Invitation to join new project"
        message = "Dear {}, {} invites you to join a new project as a developer.\nClick on the link below to join the team.\n {}".format(
            name, username, link)
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [
                  recipient_email], fail_silently=False)
        return HttpResponse()


class AddDeveloper(LoginRequiredMixin, View):
    model = ProjectParticipant
    login_url = '/accounts/login'
    redirect_field_name = '/home/'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        user = get_object_or_404(User, pk=request.GET['id'])
        if project.projectParticipant.all().filter(role="DT").count() <= 9:
            if not user.projectParticipant.all().exists():
                projectParticipant = self.model(
                    project=project, user=user, role="DT")
                projectParticipant.save()
            else:
                raise Exception("You are already a part of a projects")
        else:
            raise Exception("This Project already has 9 developers")
        return redirect(reverse('home'))
