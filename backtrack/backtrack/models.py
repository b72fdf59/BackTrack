from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

# Create your models here.


class PBI(models.Model):
    status = models.CharField(max_length=1,
                              choices=[("N", "Not Done"), ("P", "In Progress"), ("D", "Done")], default="N")
    story_points = models.FloatField()
    effort_hours = models.FloatField()
    summary = models.TextField(default=None)
    priority = models.IntegerField(default=0)
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='pbi')

    def __str__(self):
        return self.summary

    class Meta:
        db_table = "PBI"
        verbose_name = 'PBI'
        verbose_name_plural = 'PBIs'


class Project(models.Model):
    name = models.CharField(max_length=256,unique=True)
    product_owner = models.OneToOneField(User, on_delete=models.CASCADE)
    dev_team = models

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Project"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username + "'s Profile"

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, created, **kwargs):
        if not created:
            instance.profile.save()

    @receiver(pre_delete, sender=User)
    def delete_user_profile(instance, **kwargs):
        instance.profile.delete()

    class Meta:
        db_table = "User Profile"
