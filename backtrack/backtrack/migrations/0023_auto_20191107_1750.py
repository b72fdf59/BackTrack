# Generated by Django 2.2.6 on 2019-11-07 17:50

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('backtrack', '0022_auto_20191105_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pbi',
            name='status',
            field=django_fsm.FSMField(default='N', max_length=50),
        )
    ]
