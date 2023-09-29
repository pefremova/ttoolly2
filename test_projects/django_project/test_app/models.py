from django.db import models


class SomeModel(models.Model):
    field_bigint = models.BigIntegerField()
    field_binary = models.BinaryField()
    field_boolean = models.BooleanField()
    field_char = models.CharField(max_length=200)
    field_date = models.DateField(auto_now_add=True)
    field_datetime = models.DateTimeField(auto_now=True)
    field_decimal = models.DecimalField(max_digits=6, decimal_places=2)
    field_duration = models.DurationField()
    field_email = models.EmailField()
    field_float = models.FloatField()
    field_ip = models.GenericIPAddressField()
    field_integer = models.IntegerField()
    field_json = models.JSONField(null=True)
    field_positivebigint = models.PositiveBigIntegerField()
    field_positiveint = models.PositiveIntegerField()
    field_positivesmallint = models.PositiveSmallIntegerField()
    field_slug = models.SlugField()
    field_smallint = models.SmallIntegerField()
    field_text = models.TextField(blank=True)
    field_time = models.TimeField()
    field_url = models.URLField()
    field_uuid = models.UUIDField()
    field_fk = models.ForeignKey("OtherModel", on_delete=models.CASCADE, null=True)


class OtherModel(models.Model):
    field_char = models.CharField(max_length=100)


class M2MModel(models.Model):
    field_char = models.CharField(max_length=100)


class O2OModel(models.Model):
    field_char = models.CharField(max_length=100, blank=True)
