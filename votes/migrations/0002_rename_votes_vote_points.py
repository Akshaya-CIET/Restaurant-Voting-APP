# Generated by Django 4.2.1 on 2023-05-11 06:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("votes", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="vote",
            old_name="votes",
            new_name="points",
        ),
    ]
