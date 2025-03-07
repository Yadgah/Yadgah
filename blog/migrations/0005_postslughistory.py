# Generated by Django 4.2.18 on 2025-03-07 18:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0004_alter_post_slug"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostSlugHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.SlugField(allow_unicode=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="slug_history",
                        to="blog.post",
                    ),
                ),
            ],
        ),
    ]
