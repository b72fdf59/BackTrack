# Generated by Django 2.2.6 on 2019-10-27 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtrack', '0003_auto_20191026_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pbi',
            name='Project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pbi', to='backtrack.Project'),
        ),
    ]
