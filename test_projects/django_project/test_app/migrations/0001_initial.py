# Generated by Django 4.2 on 2023-09-29 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="M2MModel",
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
                ("field_char", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="O2OModel",
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
                ("field_char", models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="OtherModel",
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
                ("field_char", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="SomeModel",
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
                ("field_bigint", models.BigIntegerField()),
                ("field_binary", models.BinaryField()),
                ("field_boolean", models.BooleanField()),
                ("field_char", models.CharField(max_length=200)),
                ("field_date", models.DateField(auto_now_add=True)),
                ("field_datetime", models.DateTimeField(auto_now=True)),
                ("field_decimal", models.DecimalField(decimal_places=2, max_digits=6)),
                ("field_duration", models.DurationField()),
                ("field_email", models.EmailField(max_length=254)),
                ("field_float", models.FloatField()),
                ("field_ip", models.GenericIPAddressField()),
                ("field_integer", models.IntegerField()),
                ("field_json", models.JSONField(null=True)),
                ("field_positivebigint", models.PositiveBigIntegerField()),
                ("field_positiveint", models.PositiveIntegerField()),
                ("field_positivesmallint", models.PositiveSmallIntegerField()),
                ("field_slug", models.SlugField()),
                ("field_smallint", models.SmallIntegerField()),
                ("field_text", models.TextField(blank=True)),
                ("field_time", models.TimeField()),
                ("field_url", models.URLField()),
                ("field_uuid", models.UUIDField()),
                (
                    "field_fk",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="test_app.othermodel",
                    ),
                ),
            ],
        ),
    ]
