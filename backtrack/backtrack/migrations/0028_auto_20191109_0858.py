# Generated by Django 2.2.6 on 2019-11-09 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtrack', '0027_auto_20191109_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='projectParticipant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task', to='backtrack.ProjectParticipant'),
        ),
    ]