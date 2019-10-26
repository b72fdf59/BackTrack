from django.db import models

# Create your models here.

class PBI(models.Model):
    status = models.CharField(max_length=1,
                              choices=[("N", "Not Done"), ("P", "In Progress"), ("D", "Done")], default="N")
    story_points = models.FloatField()
    effort_hours = models.FloatField()
    summary = models.TextField(default = None)
    priority = models.IntegerField(default=0)
    Project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='pbi')

    def __str__(self):
        return self.summary

    class Meta:
        db_table = "PBI"
        verbose_name = 'PBI'
        verbose_name_plural = 'PBIs'


class Project(models.Model):
    name = models.CharField(max_length=256)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "Project"
