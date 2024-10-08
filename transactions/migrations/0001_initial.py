# Generated by Django 5.1 on 2024-09-02 12:46

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessedFile",
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
                ("file_name", models.CharField(max_length=255, unique=True)),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
                ("list_name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="UploadStatistics",
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
                ("list_name", models.CharField(max_length=255)),
                ("last_import_date", models.DateField()),
                ("records_added", models.IntegerField()),
                ("records_updated", models.IntegerField()),
                ("records_deleted", models.IntegerField()),
                ("total_active_records", models.IntegerField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("processed", models.BooleanField(default=False)),
                ("file_hash", models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="SanctionRecord",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("list_name", models.CharField(blank=True, max_length=255, null=True)),
                ("created_date", models.DateTimeField(blank=True, null=True)),
                ("modified_date", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "id_original",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "entity_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "identity_numbers",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "identity_types",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("city", models.CharField(blank=True, max_length=255, null=True)),
                ("country", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "watchlist_country",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("alias", models.CharField(blank=True, max_length=255, null=True)),
                ("alias_type", models.CharField(blank=True, max_length=255, null=True)),
                ("watch_list_id", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("dataset_id", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("no_of_variations", models.IntegerField(default=0)),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["id_original"], name="transaction_id_orig_d1a42b_idx"
                    ),
                    models.Index(
                        fields=["dataset_id"], name="transaction_dataset_0fd1bf_idx"
                    ),
                    models.Index(
                        fields=["watch_list_id"], name="transaction_watch_l_932293_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="NameVariation",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sanc_id", models.CharField(max_length=255)),
                ("algorithm", models.CharField(max_length=255)),
                ("no_of_variations", models.IntegerField(default=0)),
                ("variation", models.CharField(blank=True, max_length=255, null=True)),
                ("variation_id", models.CharField(max_length=255)),
                ("score", models.IntegerField(default=0)),
                (
                    "test_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "sanction_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variations",
                        to="transactions.sanctionrecord",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SanctionRecordDetail",
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
                ("name", models.CharField(max_length=510)),
                ("entity_type", models.CharField(max_length=50)),
                ("list_name", models.CharField(max_length=255)),
                ("score", models.IntegerField(default=0)),
                (
                    "sanction_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="transactions.sanctionrecord",
                    ),
                ),
                ("variations", models.ManyToManyField(to="transactions.namevariation")),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "balance_after_transaction",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
                ("transaction_type", models.CharField(max_length=10)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="namevariation",
            index=models.Index(
                fields=["sanc_id"], name="transaction_sanc_id_f92d4b_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="namevariation",
            index=models.Index(
                fields=["variation_id"], name="transaction_variati_fa4c76_idx"
            ),
        ),
    ]
