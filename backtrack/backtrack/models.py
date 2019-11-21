from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django_fsm import FSMField, transition

# Create your models here.


class PBI(models.Model):
    # status = models.CharField(max_length=1,
    #                           choices=[("N", "Not Done"), ("P", "In Progress"), ("D", "Done")], default="N")
    status = FSMField(default='N')
    story_points = models.FloatField()
    effort_hours = models.FloatField()
    summary = models.TextField(default=None)
    priority = models.IntegerField(default=0)
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='pbi')
    sprint = models.ForeignKey(
        'Sprint', on_delete=models.CASCADE, related_name='pbi', null=True, blank=True)

    @transition(field=status, source='N', target='P')
    def addToSprint(self, sprint):
        self.sprint = sprint

    @transition(field=status, source='P', target='N')
    def removeToSprint(self, sprint):
        self.sprint = None

    @transition(field=status, source='P', target='D')
    def markDone(self):
        pass

    # can implement transition unfinished if need be

    def delete(self, *args, **kwargs):
        pbiList = self.project.pbi.all().exclude(status="D")
        for pbi in pbiList:
            if pbi.priority > self.priority:
                pbi.priority -= 1
                pbi.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.summary

    class Meta:
        db_table = "PBI"
        verbose_name = 'PBI'
        verbose_name_plural = 'PBIs'


class Project(models.Model):
    name = models.CharField(max_length=256, unique=True)
    complete = models.BooleanField(default=False)

    # Please add Dev Team through this method
    def add_dev_team(self, dev_team):
        # Put logic to not allow more than 9 team members (Not sure if correct)
        if self.projectParticipant.filter(role__exact="DT").user.count() >= 9:
            raise Exception("Too many developers")
        self.project_set.user = dev_team

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Project"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

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


class ProjectParticipant(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projectParticipant")
    role = models.CharField(max_length=2, choices=[(
        "SM", "Scrum Master"), ("PO", "Product Owner"), ("DT", "Development Team")])
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="projectParticipant")

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ['user', 'project']
        # permissions=[]
        # if role=="PO":
        #     permissions= ['can add PBI', 'can edit PBI']
        # else:
        #     permissions= []


class Sprint(models.Model):
    capacity = models.FloatField()
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='sprint')
    start = models.DateField(
        auto_now=False, auto_now_add=False, blank=False)
    end = models.DateField(auto_now=False, auto_now_add=False, blank=False)

    @property
    def available(self):
        from datetime import date
        now = date.today()
        return now <= self.end

    @property
    def remainingCapacity(self):
        from django.db.models import Sum
        myDict = self.pbi.all().aggregate(Sum('story_points'))
        usedCapacity = myDict['story_points__sum']
        if not usedCapacity:
            usedCapacity = 0
        return self.capacity - usedCapacity

    # @property
    # def remainingCapacity(self):
    #     from django.db.models import Sum
    #     myDict = self.pbi.all().aggregate(Sum('effort_hours'))
    #     hoursCompleted = myDict['effort_hours__sum']
    #     if not hoursCompleted:
    #         hoursCompleted = 0
    #     return self.capacity - hoursCompleted

    @property
    def count(self):
        return self.project.sprint.filter(start__lte=self.start).count()

    def get_absolute_url(self):
        return reverse("detail-sprint", kwargs={"pk": self.project_id, "spk": self.id})


class Task(models.Model):
    # status = models.CharField(max_length=1,
    #                           choices=[("N", "Not Done"), ("P", "In Progress"), ("D", "Done")], default="N")
    status = FSMField(default='N')
    # story_points = models.FloatField()
    effort_hours = models.FloatField()
    summary = models.TextField(default=None)
    pbi = models.ForeignKey(
        'PBI', on_delete=models.CASCADE, related_name='task')
    # sprint = models.ForeignKey(
    #     'Sprint', on_delete=models.CASCADE, related_name='task_sprint', null=True, blank=True)
    projectParticipant = models.ForeignKey(
        'ProjectParticipant', on_delete=models.CASCADE, related_name='task', null=True, blank=True)

    @transition(field=status, source='N', target='P')
    def putInProgress(self, pp):
        print(pp)
        if self.projectParticipant:
            pass
        else:
            self.projectParticipant = pp
            pass

    @transition(field=status, source='P', target='D')
    def putInDone(self, pp):
        # print(pp)
        # self.projectParticipant = pp
        pass

    @transition(field=status, source='P', target='N')
    def putInNotDone(self, pp):
        print(pp)
        if self.projectParticipant:
            pass
        else:
            self.projectParticipant = pp
            pass

    def __str__(self):
        return self.summary

    class Meta:
        db_table = "Task"
