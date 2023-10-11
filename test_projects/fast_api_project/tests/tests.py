from ..tests import client, db
from ttoolly.testcases import CasesAdd
from ttoolly.generator import TestCaseMeta
from ttoolly.elements.rest import Form
from ttoolly.adapters.pytest import Actions
import datetime
from ..app import sql_schemas


class TestPytest(Actions, metaclass=TestCaseMeta):
    cases = [
        CasesAdd,
    ]
    form = Form(
        **{
            "fields": {
                "field_boolean": {
                    "not_empty": True,
                    "only": None,
                    "required": True,
                    "type": "bool",
                    "unique": False,
                },
                "field_date": {
                    "lt": [],
                    "lte": [],
                    "not_empty": False,
                    "only": None,
                    "required": False,
                    "step": datetime.timedelta(days=1),
                    "type": "date",
                    "unique": False,
                },
                "field_datetime": {
                    "lt": [],
                    "lte": [],
                    "not_empty": False,
                    "only": None,
                    "required": True,
                    "step": datetime.timedelta(seconds=1),
                    "type": "datetime",
                    "unique": False,
                },
                "field_decimal": {
                    "lt": [],
                    "lte": [],
                    "max_decimal_places": 1,
                    "not_empty": False,
                    "only": None,
                    "required": False,
                    "step": "0.1",
                    "type": "decimal",
                    "unique": False,
                },
                "field_integer": {
                    "lt": [],
                    "lte": [],
                    "not_empty": False,
                    "only": None,
                    "required": False,
                    "step": 1,
                    "type": "int",
                    "unique": False,
                },
                "field_str": {
                    "max_length": 200,
                    "min_length": 1,
                    "not_empty": True,
                    "null_allowed": True,
                    "only": None,
                    "required": True,
                    "str_format": None,
                    "type": "str",
                    "unique": True,
                },
            }
        }
    )

    url_add = "/items/create/"

    def get_all_form_errors(self, response):
        if response.status_code >= 300 or response.status_code < 200:
            return response.json()

    def get_objects_count(self):
        return db.query(sql_schemas.Item).count()

    def get_objects_pks(self):
        return []

    def prepare_for_add(self):
        pass

    def send_add(self, params: dict):
        for field in ("field_decimal",):
            if field in params.keys() and params[field] is not None:
                params[field] = str(params[field])
        return client.post(self.url_add, json=params)
