from ..models import Sprint, Project, PBI, Task
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from ..helpers import addContext
from django.views.generic import CreateView, View, TemplateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import json


class AddTask(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    # pk_url_kwarg = 'pbipk'
    model = Task
    fields = ['summary', 'effort_hours']
    login_url = '/accounts/login'
    template_name = "backtrack/addTask.html"
    success_message = "Task was created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add context variables for sidebar
        context = addContext(self, context)

        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        pbi = get_object_or_404(PBI, pk=self.kwargs['pbipk'])
        context['Sprint'] = sprint
        context['PBI'] = pbi
        return context

    def get_success_url(self):
        # Redirect to Sprint Detail
        return reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']})

    def form_valid(self, form):
        # Add PBI and Project to task before saving
        form.instance.pbi = get_object_or_404(
            PBI, pk=self.kwargs['pbipk'])
        return super().form_valid(form)


class DetailTask(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    pk_url_kwarg = 'taskpk'
    model = Task
    fields = ['summary', 'effort_hours', 'projectParticipant']
    login_url = '/accounts/login'
    template_name = 'backtrack/Taskdetail.html'
    success_message = "Task was updated"

    def get_context_data(self, **kwargs):
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        context = super().get_context_data(**kwargs)
        context['Task'] = self.object
        context['sprint'] = sprint
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

    def get_success_url(self):
        # Redirect to Sprint Backlog
        return reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']})

    def test_func(self):
        # Get User
        user = self.request.user
        # Get project from the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if user.projectParticipant.filter(project__complete=False).exists():
            userProject = user.projectParticipant.get(
                project__complete=False).project
            return userProject.pk == project.pk
        return False


class AddTaskToInProgress(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "Successfully changed Task status to In Progress"

    def post(self, request, *args, **kwargs):
        if request.POST.get('Task') and request.POST.get('ProjectID'):
            # If post request is sent from Detail Page
            taskid = request.POST.get('Task')
            projectid = request.POST.get('ProjectID')
            sprintid = request.POST.get('SprintID')
            task = get_object_or_404(Task, pk=taskid)
            confirmed = task.putInProgress(
                self.request.user.projectParticipant.get(project_id=projectid))

            if confirmed:
                task.save()
                messages.success(
                    self.request, "Successfully changed Task status to In Progress")
                return redirect(reverse('detail-sprint', kwargs={'pk': projectid, 'spk': sprintid}))
            else:
                messages.error(
                    self.request, "No ProjectParticipant is in charge of the Task")
                return redirect(reverse('detail-sprint', kwargs={'pk': projectid, 'spk': sprintid}))

        else:
            # json sent
            data = json.loads(request.body)
            taskid = data['Task']
            projectid = data['ProjectID']
            task = get_object_or_404(Task, pk=taskid)
            confirmed = task.putInProgress(
                self.request.user.projectParticipant.get(project_id=projectid))

            if confirmed:
                task.save()
                response = JsonResponse(
                    {"success": "Successfully changed Task status to In Progress"})
                return response
            else:
                response = JsonResponse(
                    {"error": "No ProjectParticipant is in charge of the Task"})
                response.status_code = 400
                return response


class AddTaskToDone(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "Successfully changed Task status to Done"

    def post(self, request, *args, **kwargs):
        if request.POST.get('Task') and request.POST.get('ProjectID'):
            # If post request is sent from Detail Page
            taskid = request.POST.get('Task')
            projectid = request.POST.get('ProjectID')
            sprintid = request.POST.get('SprintID')
            task = get_object_or_404(Task, pk=taskid)
            confirmed = task.putInDone()

            if confirmed:
                task.save()

                if not self.request.user.projectParticipant.filter(
                        project__complete=False).exists():
                    # If project is complete then redirect to home
                    messages.success(request, "Project Completed Successfully!")
                    return redirect(reverse('home'))

                messages.success(
                    self.request, "Successfully changed Task status to Done")
                return redirect(reverse('detail-sprint', kwargs={'pk': projectid, 'spk': sprintid}))
            else:
                messages.error(
                    self.request, "No ProjectParticipant is in charge of the Task")
                return redirect(reverse('detail-sprint', kwargs={'pk': projectid, 'spk': sprintid}))

        else:
            # json sent
            data = json.loads(request.body)
            taskid = data['Task']
            projectid = data['ProjectID']
            task = get_object_or_404(Task, pk=taskid)
            confirmed = task.putInDone()

            if confirmed:
                task.save()

                if not self.request.user.projectParticipant.filter(
                        project__complete=False).exists():
                    # If project is complete then redirect to home
                    response = JsonResponse(
                        {"success": "Project Completed Successfully!", "status_code": 302})
                    return response

                response = JsonResponse(
                    {"success": "Successfully changed Task status to Done", "status_code": 200})
                return response
            else:
                response = JsonResponse(
                    {"error": "No ProjectParticipant is in charge of the Task"})
                response.status_code = 400
                return response


class AddTaskToNotDone(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "Successfully changed Task status to Not Done"

    def post(self, request, *args, **kwargs):
        if request.POST.get('Task') and request.POST.get('ProjectID'):
            # If post request is sent from Detail Page
            taskid = request.POST.get('Task')
            projectid = request.POST.get('ProjectID')
            sprintid = request.POST.get('SprintID')
            task = get_object_or_404(Task, pk=taskid)
            confirmed = task.putInNotDone()

            if confirmed:
                task.save()
                messages.success(
                    self.request, "Successfully changed Task status to Not Done")
                return redirect(reverse('detail-sprint', kwargs={'pk': projectid, 'spk': sprintid}))
            else:
                messages.error(
                    self.request, "No ProjectParticipant is in charge of the Task")
                return redirect(reverse('detail-sprint', kwargs={'pk': projectid, 'spk': sprintid}))

        else:
            # json sent
            data = json.loads(request.body)
            taskid = data['Task']
            projectid = data['ProjectID']
            task = get_object_or_404(Task, pk=taskid)
            confirmed = task.putInNotDone()

            if confirmed:
                task.save()
                response = JsonResponse(
                    {"success": "Successfully changed Task status to Not Done"})
                return response
            else:
                response = JsonResponse(
                    {"error": "No ProjectParticipant is in charge of the Task"})
                response.status_code = 400
                return response


class DeleteTask(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    template_name = 'backtrack/task_confirm_delete.html'
    model = Task
    login_url = '/accounts/login'
    pk_url_kwarg = 'taskpk'
    success_message = "Task was deleted"

    def get_success_url(self):
        return reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Task'] = self.object
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        # Get User
        user = self.request.user
        # Get project from the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if user.projectParticipant.filter(project__complete=False).exists():
            userProject = user.projectParticipant.get(
                project__complete=False).project
            return userProject.pk == project.pk
        return False
