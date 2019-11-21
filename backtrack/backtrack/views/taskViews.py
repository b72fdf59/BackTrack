from ..models import Sprint, Project, PBI, Task
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
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
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        pbi = get_object_or_404(PBI, pk=self.kwargs['pbipk'])
        context = super().get_context_data(**kwargs)
        context = addContext(self, context)
        context['sprint'] = sprint
        context['pbi'] = pbi
        return context

    def get_success_url(self):
        return "{}?all=0".format(reverse('detail-sprint', kwargs={'pk': self.object.project.id, 'spk': self.kwargs['spk']}))

    def form_valid(self, form):
        form.instance.pbi = get_object_or_404(
            PBI, pk=self.kwargs['pbipk'])
        form.instance.project = get_object_or_404(
            Project, pk=self.kwargs['pk'])
        # form.instance.sprint = get_object_or_404(
        #     Sprint, pk=self.kwargs['pk'])
        return super().form_valid(form)


class UpdateTaskNotDone(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    pk_url_kwarg = 'taskpk'
    model = Task
    fields = ['status', 'summary', 'effort_hours', 'projectParticipant']
    login_url = '/accounts/login'
    template_name = 'backtrack/Taskdetail.html'
    success_message = "Task was updated"

    def get_context_data(self, **kwargs):
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        context = super().get_context_data(**kwargs)
        context['Task'] = self.object
        context['sprint'] = sprint
        context = addContext(self, context)
        return context

    def get_success_url(self):
        return "{}?all=0".format(reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']}))

    def form_valid(self, form):
        UpdateTask = self.model.objects.get(pk=self.kwargs['taskpk'])
        return super().form_valid(form)

class UpdateTaskinProgress(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    pk_url_kwarg = 'taskpk'
    model = Task
    fields = ['status']
    login_url = '/accounts/login'
    template_name = 'backtrack/Taskdetail_inProgress.html'
    success_message = "Task was updated"

    def get_context_data(self, **kwargs):
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        context = super().get_context_data(**kwargs)
        context['Task'] = self.object
        context['sprint'] = sprint
        context = addContext(self, context)
        return context

    def get_success_url(self):
        return "{}?all=0".format(reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']}))

    def form_valid(self, form):
        UpdateTask = self.model.objects.get(pk=self.kwargs['taskpk'])
        return super().form_valid(form)


class AddTaskToInProgress(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "Successfully changed Task status to In Progress"

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        taskid = data['Task']
        projectid = data['ProjectID']
        # print(data)
        task = get_object_or_404(Task, pk=taskid)
        x = task.putInProgress(
            self.request.user.projectParticipant.get(project_id=projectid))
        if not x:
            task.save()
            response = JsonResponse(
                {"success": "Successfully changed Task status to In Progress"})
            return response
        else:
            response = JsonResponse(
                {"error": "No ProjectParticipant is in-charge of the Task"})
            response.status_code = 400
            return response


class AddTaskToDone(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "Successfully changed Task status to Done"

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        taskid = data['Task']
        projectid = data['ProjectID']
        # print(data)
        task = get_object_or_404(Task, pk=taskid)
        task.putInDone(
            self.request.user.projectParticipant.get(project_id=projectid))
        task.save()
        response = JsonResponse(
            {"success": "Successfully changed Task status to Done"})
        return response


class AddTaskToNotDone(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "Successfully changed Task status to Not Done"

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        taskid = data['Task']
        projectid = data['ProjectID']
        # print(data)
        task = get_object_or_404(Task, pk=taskid)
        task.putInNotDone(
            self.request.user.projectParticipant.get(project_id=projectid))
        task.save()
        response = JsonResponse(
            {"success": "Successfully changed Task status to Not Done"})
        return response


class DeleteTask(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = 'backtrack/task_confirm_delete.html'
    model = Task
    login_url = '/accounts/login'
    pk_url_kwarg = 'taskpk'
    success_message = "Task was deleted"

    def get_success_url(self):
        return "{}?all=0".format(reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Task'] = self.object
        context = addContext(self, context)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)