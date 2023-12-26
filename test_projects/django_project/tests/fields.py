from faker import Faker
from ttoolly.elements.common import FieldStr, Field, FieldSelect
from ttoolly.utils.randomizer import get_randname
import json


fake = Faker()


class FieldUrl(FieldStr):
    type_of = "url"

    def get_random_value(self, length=None):
        return fake.url()


class FieldIP(FieldStr):
    type_of = "ip"

    def get_random_value(self, length=None):
        return fake.ipv4()


class FieldJSON(Field):
    type_of = "json"

    def get_random_value(self, length=None):
        return json.dumps({get_randname(10, "wd"): get_randname(10, "wd")})


class FieldSelect(FieldSelect):
    type_of = "choice_fk"

    def get_random_value(self, *a, **k):
        from test_app.models import OtherModel

        return OtherModel.objects.create().pk
