# Generated by Django 2.2.6 on 2019-11-04 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backtrack', '0016_auto_20191104_0738'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectparticipant',
            unique_together=set(),
        ),
    ]