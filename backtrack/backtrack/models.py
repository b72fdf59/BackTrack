from django.db import models

# Create your models here.


class ProductBacklog(models.Model):
    PBI = models.ForeignKey('PBI', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['Project', 'PBI'], name="project_PBI")
        ]


class PBI(models.Model):
    status = models.CharField(max_length=1,
                              choices=[("N", "Not Done"), ("P", "In Progress"), ("D", "Done")], default="N")
    story_points = models.PositiveSmallIntegerField()
    effort_hours = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "PBI"
        verbose_name = 'PBI'
        verbose_name_plural = 'PBIs'


class Project(models.Model):
    pass
