from ..models import PBI, Project
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from ..helpers import addContext, getPBIfromProj
from django.contrib.messages.views import SuccessMessageMixin


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


class ProductBacklogView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login'
    template_name = 'backtrack/pb.html'

    def get_context_data(self, **kwargs):
        import math
        # Get query parameter 'all' which is 1 or 0
        # If not present then pass 0
        # 1:Get all PBIs for a project
        # 0: Exclude PBI which are Done
        data = getPBIfromProj(
            kwargs['pk'], self.request.GET['all'] if 'all' in self.request.GET else '0')

        # Sort PBI according to priority, put the PBI that are done at the end of the backlog
        data = sorted(data, key=lambda x: (
            x.priority if x.status != "D" else math.inf, x.summary))

        # Calculate the total story points and effort hours
        sum_effort_hours, sum_story_points = 0, 0
        for PBIObj in data:
            sum_effort_hours += PBIObj.effort_hours
            sum_story_points += PBIObj.story_points
            PBIObj.sum_effort_hours = sum_effort_hours
            PBIObj.sum_story_points = sum_story_points

        context = {'data': data}
        context = addContext(self, context)
        return context


class AddPBI(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PBI
    fields = ['summary', 'story_points', 'effort_hours']
    login_url = '/accounts/login'
    template_name = "backtrack/addPBI.html"
    success_message = "PBI was created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

    def get_success_url(self):
        # Redirect to the product backlog
        return "{}?all=0".format(reverse('pb', kwargs={'pk': self.object.project.id}))

    def form_valid(self, form):
        # Get all PBI that are not done
        PBIData = getPBIfromProj(self.kwargs['pk'], '0')

        # Initialise Priority
        priority = 0
        # Sort According to Priority
        PBIData = sorted(PBIData, key=lambda x: (
            x.priority), reverse=True)
        # If no Item in list make priority 1
        if PBIData:
            priority = PBIData[0].priority + 1
        else:
            priority = 1

        # Assign the priority to the form object before saving
        form.instance.priority = priority
        # Assign the project to the form object before saving
        form.instance.project = get_object_or_404(
            Project, pk=self.kwargs['pk'])
        return super().form_valid(form)


class updatePBI(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    pk_url_kwarg = 'pbipk'
    model = PBI
    fields = ['priority', 'summary', 'story_points', 'effort_hours']
    login_url = '/accounts/login'
    template_name = 'backtrack/PBIdetail.html'
    success_message = "PBI was updated"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PBI'] = self.object
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

    def get_success_url(self):
        # Redirect to the product backlog
        return "{}?all=0".format(reverse('pb', kwargs={'pk': self.kwargs['pk']}))

    def form_valid(self, form):
        # Get PBI from its primary key
        updatePBI = self.model.objects.get(pk=self.kwargs['pbipk'])
        # Get all PBI that are not done
        PBIList = getPBIfromProj(self.kwargs['pk'], '0')

        # PBI to be removed
        remove = []
        priorityData = form.cleaned_data['priority']
        if int(priorityData) < updatePBI.priority:
            # Remove all PBI with priority higher than post data priority
            # and lesser or equal than current PBI priority
            for PBIObj in PBIList:
                if PBIObj.priority < int(priorityData) or PBIObj.priority >= updatePBI.priority:
                    remove.append(PBIObj.priority)
            PBIList = [
                PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Increase each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority += 1
                PBIObj.save()
        else:
            # Remove all PBI with priority higher than post PBI priority
            # and lesser than and equal to Post data priority
            for PBIObj in PBIList:
                if PBIObj.priority <= updatePBI.priority or PBIObj.priority > int(priorityData):
                    remove.append(PBIObj.priority)
            PBIList = [
                PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Decrease each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority -= 1
                PBIObj.save()

        return super().form_valid(form)


class DeletePBI(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = 'backtrack/pbi_confirm_delete.html'
    model = PBI
    login_url = '/accounts/login'
    pk_url_kwarg = 'pbipk'
    success_message = "PBI was deleted"

    def get_success_url(self):
        # Redirect to the product backlog
        return "{}?all=0".format(reverse('pb', kwargs={'pk': self.object.project.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PBI'] = self.object
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
