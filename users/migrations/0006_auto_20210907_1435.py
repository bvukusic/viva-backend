# Generated by Django 3.1.3 on 2021-09-07 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210906_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertimelineentry',
            name='mood',
            field=models.CharField(blank=True, choices=[('terrible', 'Terrible'), ('bad', 'Bad'), ('neutral', 'Neutral'), ('good', 'Good'), ('great', 'Great')], max_length=30, null=True),
        ),
    ]
