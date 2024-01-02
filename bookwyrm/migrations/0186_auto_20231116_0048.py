# Generated by Django 3.2.20 on 2023-11-16 00:48

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("bookwyrm", "0185_alter_notification_notification_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParentJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("task_id", models.UUIDField(blank=True, null=True, unique=True)),
                (
                    "created_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("complete", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("complete", "Complete"),
                            ("stopped", "Stopped"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="user_import_time_limit",
            field=models.IntegerField(default=48),
        ),
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("FAVORITE", "Favorite"),
                    ("BOOST", "Boost"),
                    ("REPLY", "Reply"),
                    ("MENTION", "Mention"),
                    ("TAG", "Tag"),
                    ("FOLLOW", "Follow"),
                    ("FOLLOW_REQUEST", "Follow Request"),
                    ("IMPORT", "Import"),
                    ("USER_IMPORT", "User Import"),
                    ("USER_EXPORT", "User Export"),
                    ("ADD", "Add"),
                    ("REPORT", "Report"),
                    ("LINK_DOMAIN", "Link Domain"),
                    ("INVITE", "Invite"),
                    ("ACCEPT", "Accept"),
                    ("JOIN", "Join"),
                    ("LEAVE", "Leave"),
                    ("REMOVE", "Remove"),
                    ("GROUP_PRIVACY", "Group Privacy"),
                    ("GROUP_NAME", "Group Name"),
                    ("GROUP_DESCRIPTION", "Group Description"),
                    ("MOVE", "Move"),
                ],
                max_length=255,
            ),
        ),
        migrations.CreateModel(
            name="BookwyrmExportJob",
            fields=[
                (
                    "parentjob_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="bookwyrm.parentjob",
                    ),
                ),
                ("export_data", models.FileField(null=True, upload_to="")),
            ],
            options={
                "abstract": False,
            },
            bases=("bookwyrm.parentjob",),
        ),
        migrations.CreateModel(
            name="BookwyrmImportJob",
            fields=[
                (
                    "parentjob_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="bookwyrm.parentjob",
                    ),
                ),
                ("archive_file", models.FileField(blank=True, null=True, upload_to="")),
                ("import_data", models.JSONField(null=True)),
                (
                    "required",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=50),
                        blank=True,
                        size=None,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("bookwyrm.parentjob",),
        ),
        migrations.CreateModel(
            name="ChildJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("task_id", models.UUIDField(blank=True, null=True, unique=True)),
                (
                    "created_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("complete", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("complete", "Complete"),
                            ("stopped", "Stopped"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "parent_job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="child_jobs",
                        to="bookwyrm.parentjob",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="notification",
            name="related_user_export",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bookwyrm.bookwyrmexportjob",
            ),
        ),
    ]
