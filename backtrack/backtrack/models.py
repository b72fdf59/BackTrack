from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django_fsm import FSMField, transition
from django.http import JsonResponse
# Create your models here.


class PBI(models.Model):
    status = FSMField(default='N')
    story_points = models.FloatField()
    effort_hours = models.FloatField()
    summary = models.TextField(default=None)
    priority = models.IntegerField(default=0)
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='pbi')
    sprint = models.ForeignKey(
        'Sprint', on_delete=models.CASCADE, related_name='pbi', null=True, blank=True)

    @property
    def burndown(self):
        from django.db.models import Sum
        myDict = self.task.filter(
            status__exact="D").aggregate(Sum('effort_hours'))
        remainingHours = myDict['effort_hours__sum']
        if not remainingHours:
            remainingHours = 0
        return remainingHours

    @property
    def TotalTaskHours(self):
        TaskHours = 0
        TaskList = self.task.all()
        for task in TaskList:
            if task.pbi.id == self.id:
                TaskHours += task.effort_hours
        return TaskHours


    @property
    def remainingEffortHours(self):
        return self.effort_hours - self.burndown

    @transition(field=status, source=['N', 'U'], target='P')
    def addToSprint(self, sprint):
        self.sprint = sprint

    @transition(field=status, source='P', target='N')
    def removeFromSprint(self, sprint):
        self.sprint = None

    @transition(field=status, source='P', target='N')
    def markNotDone(self):
        pass

    @transition(field=status, source='P', target='D')
    def markDone(self):
        self.delete(transition=1)
        self.priority = 0

    @transition(field=status, source='P', target='U')
    def markUnfinished(self):
        self.sprint = None

    # can implement transition unfinished if need be

    def delete(self, *args, **kwargs):
        pbiList = self.project.pbi.all().exclude(status="D")
        for pbi in pbiList:
            if pbi.priority > self.priority:
                pbi.priority -= 1
                pbi.save()
        if not hasattr(kwargs, "transition"):
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
    role = models.CharField(max_length=1, choices=[(
        "D", "Developer"), ("M", "Manager")])

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
    complete = models.BooleanField(default=False)

    @property
    def available(self):
        return not self.complete

    @property
    def remainingCapacity(self):
        from django.db.models import Sum
        myDict = self.pbi.all().aggregate(Sum('story_points'))
        usedCapacity = myDict['story_points__sum']
        if not usedCapacity:
            usedCapacity = 0
        return self.capacity - usedCapacity

    @property
    def count(self):
        return self.project.sprint.filter(start__lte=self.start).count()

    @property
    def remainingHours(self):
        from django.db.models import Sum
        # Get hours of all PBI that are not complete
        PBIList = self.pbi.all().exclude(status__exact="D")
        remainingHours = 0
        for PBI in PBIList:
            remainingHours += PBI.remainingEffortHours
        return remainingHours

    @property
    def remainingDays(self):
        from datetime import date
        if self.complete:
            return 0
        now = date.today()
        remDays = self.end - now
        if remDays.days < 0:
            return 0
        return remDays.days

    def get_absolute_url(self):
        return reverse("detail-sprint", kwargs={"pk": self.project_id, "spk": self.id})


class Task(models.Model):
    status = FSMField(default='N')
    effort_hours = models.FloatField()
    summary = models.TextField(default=None)
    pbi = models.ForeignKey(
        'PBI', on_delete=models.CASCADE, related_name='task')
    projectParticipant = models.ForeignKey(
        'ProjectParticipant', on_delete=models.CASCADE, related_name='task', null=True, blank=True)

    @transition(field=status, source='N', target='P')
    def putInProgress(self, pp):
        if self.projectParticipant:
            return True
        else:
            return False

    @transition(field=status, source='P', target='D')
    def putInDone(self):
        return True

    @transition(field=status, source='P', target='N')
    def putInNotDone(self):
        if self.projectParticipant:
            self.projectParticipant = None
        return True

    def __str__(self):
        return self.summary

    class Meta:
        db_table = "Task"


@receiver(post_save, sender=Task, dispatch_uid="complete_PBI")
def completePBI(sender, instance, **kwargs):
    if not instance.pbi.task.all().exclude(status__exact="D").exists():
        pbi = instance.pbi
        pbi.markDone()
        pbi.save()
        if not pbi.project.pbi.all().exclude(status__exact="D").exists():
            pbi.project.complete = True
            pbi.project.save()