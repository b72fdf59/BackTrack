# Not being used might be used later
from django import forms
from .models import Sprint, Task, ProjectParticipant, Project


class CreateSprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['capacity', 'start', 'end']
        widgets = {
            'start': forms.SelectDateWidget(),
            'end': forms.SelectDateWidget()
        }


class TaskDetailForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['summary', 'effort_hours', 'projectParticipant']

    def __init__(self, *args, **kwargs):
        projectID = kwargs.pop('Project')
        project = Project.objects.get(pk=projectID)
        super().__init__(*args, **kwargs)

        if project:
            self.fields['projectParticipant'].queryset = project.projectParticipant.filter(
                role__exact="DT")
