# Generated by Django 4.2.18 on 2025-03-05 20:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0002_label_is_custom"),
    ]

    operations = [
        migrations.AddField(
            model_name="label",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="labels",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="label",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name="label",
            unique_together={("name", "created_by")},
        ),
    ]
