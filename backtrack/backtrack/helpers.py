from django.contrib.auth.models import User
from .models import PBI


def addContext(self, context):
    context['Project'] = self.request.user.projectParticipant.get(
        project__complete=False).project
    context['ProjectParticipant'] = self.request.user.projectParticipant.get(
        project__complete=False)
    context['Sprints'] = self.request.user.projectParticipant.get(
        project__complete=False).project.sprint.all().order_by('start')
    return context


def getPBIfromProj(pk, all):
    data, pbiList = [], PBI.objects.filter(project_id=pk)
    # If all is true then do not count objects with status done(which are finished), this is for when creating a new PBI
    if (not bool(int(all))):
        pbiList = pbiList.exclude(status__contains="D")
    return pbiList
