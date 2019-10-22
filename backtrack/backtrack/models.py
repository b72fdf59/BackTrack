from django.db import models

# Create your models here.


class ProductBacklog(models.Model):
    PBI = models.ForeignKey('PBI', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    class Meta:
        db_table = "Product Backlog"
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'PBI'], name="project_PBI")
        ]


class PBI(models.Model):
    status = models.CharField(max_length=1,
                              choices=[("N", "Not Done"), ("P", "In Progress"), ("D", "Done")], default="N")
    story_points = models.FloatField()
    effort_hours = models.FloatField()
    summary = models.TextField(default = None)
    priority = models.IntegerField(default=0)

    class Meta:
        db_table = "PBI"
        verbose_name = 'PBI'
        verbose_name_plural = 'PBIs'


class Project(models.Model):
    name = models.CharField(max_length=256)
    
    class Meta:
        db_table = "Project"
