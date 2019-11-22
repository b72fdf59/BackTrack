from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Project, ProjectParticipant
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from ..helpers import addContext
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


class CreateProject(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Project
    fields = ['name']
    login_url = '/accounts/login'
    template_name = "backtrack/createProject.html"
    success_message = "Project was created"

    def get_success_url(self):
        # Redirect to invite members page
        return reverse('invite-project-members', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        response = super().form_valid(form)

        # Create a project participant of the user as a Product Owner
        projectParticipant = ProjectParticipant(
            user=self.request.user, role="PO", project=form.instance)
        projectParticipant.save()
        return response


class InviteMember(LoginRequiredMixin, TemplateView):
    template_name = "backtrack/inviteMembers.html"
    login_url = '/accounts/login'

    def get_context_data(self, **kwargs):
        context = {}
        # Get all users other than the current user
        users = User.objects.all().exclude(username=self.request.user.username)

        for user in users:
            if user.projectParticipant.all().exists:
                if user.projectParticipant.filter(project__complete=False).exists():
                    # If a user has a project which is not complete exclude him.
                    users = users.exclude(pk=user.pk)
        context['users'] = users
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

# Send Email to team member


class EmailMember(LoginRequiredMixin, View):
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        userID = self.request.GET['id']
        recipient_email = get_object_or_404(User, id=userID).email
        if recipient_email:
            # If the recepient mail exists
            username = self.request.user.username
            name = User.objects.get(id=userID).username
            # Build absolute URL for the invite link
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
        else:
            return HttpResponseForbidden("User does not have an email")


class AddDeveloper(LoginRequiredMixin, View):
    model = ProjectParticipant
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        user = get_object_or_404(User, pk=request.GET['id'])
        if project.projectParticipant.all().filter(role="DT").count() <= 9:
            # If there are lesser than 9 project participants
            if not user.projectParticipant.filter(project__complete=False).exists():
                # If the user has projects that are not complete
                projectParticipant = self.model(
                    project=project, user=user, role="DT")
                projectParticipant.save()
            else:
                raise Exception("You are already a part of a projects")
        else:
            raise Exception("This Project already has 9 developers")
        messages.success(request, 'Successfully joined project')
        return redirect(reverse('home'))
