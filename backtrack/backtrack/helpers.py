from django.contrib.auth.models import User

def addContext(self, context):
    context['Project'] = self.request.user.projectParticipant.get(
        project__complete=False).project
    context['ProjectParticipant'] = self.request.user.projectParticipant.get(
        project__complete=False)
    context['Sprints'] = self.request.user.projectParticipant.get(
        project__complete=False).project.sprint.all().order_by('start')
    return context
