from django.contrib.auth.models import User
from .models import PBI


def addContext(self, context):
    #Get that project by a project participant which has not been completed
    context['Project'] = self.request.user.projectParticipant.get(
        project__complete=False).project
        #Get the project participant whose project is not completed
    context['ProjectParticipant'] = self.request.user.projectParticipant.get(
        project__complete=False)
        #Get all the sprints for a particular project and order them by their start date
    context['Sprints'] = self.request.user.projectParticipant.get(
        project__complete=False).project.sprint.all().order_by('start')
    return context


def getPBIfromProj(pk, all):
    data, pbiList = [], PBI.objects.filter(project_id=pk)
    # If all is true then do not count objects with status done(which are finished), this is for when creating a new PBI
    if (not bool(int(all))):
        pbiList = pbiList.exclude(status__contains="D")
    return pbiList
