from django.contrib import admin

from .models import PBI,ProductBacklog,Project

# Register your models here.
admin.site.register(PBI)
admin.site.register(Project)
admin.site.register(ProductBacklog)