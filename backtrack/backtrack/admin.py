from django.contrib import admin

from .models import PBI,Project,Profile, ProjectParticipant, Sprint

# Register your models here.
admin.site.register(PBI)
admin.site.register(Project)
admin.site.register(Profile)
admin.site.register(ProjectParticipant)
admin.site.register(Sprint)