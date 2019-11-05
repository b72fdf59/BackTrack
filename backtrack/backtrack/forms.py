#Not being used might be used later
from django import forms
from .models import Sprint
class CreateSprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['capacity', 'start', 'end']
        widgets = {
            'start': forms.SelectDateWidget(),
            'end': forms.SelectDateWidget()
        }