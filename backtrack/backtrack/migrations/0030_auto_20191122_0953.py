# Generated by Django 2.2.6 on 2019-11-22 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtrack', '0029_auto_20191122_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='pbi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='backtrack.PBI'),
        ),
    ]