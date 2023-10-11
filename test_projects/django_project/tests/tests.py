from django.contrib.auth.models import User
from django.test import TestCase
from test_app.models import SomeModel
from ttoolly.adapters.django import Actions as DjangoActions
from ttoolly.adapters.django_pytest import Actions as PytestActions
from ttoolly.elements.django import FormDjango
from ttoolly.generator import TestCaseMeta
from ttoolly.loaders import JsonLoader
from ttoolly.testcases import CasesAdd

form_description = FormDjango(**JsonLoader("tests/test_config.json").data)


class TestUnittest(TestCase, DjangoActions, metaclass=TestCaseMeta):
    cases = [
        CasesAdd,
    ]
    form = form_description
    model = SomeModel
    status_code_add_success = 302
    url_add = "/admin/test_app/somemodel/add/"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser("admin", "admin@test.test", "test")

    def setUp(self) -> None:
        self.client.force_login(self.user)


class TestPytest(PytestActions, metaclass=TestCaseMeta):
    cases = [
        CasesAdd,
    ]
    additional_test_fixtures = ["client", "admin_user"]
    form = form_description
    model = SomeModel
    status_code_add_success = 302
    url_add = "/admin/test_app/somemodel/add/"

    def prepare_for_add(self, **kwargs):
        kwargs["client"].force_login(kwargs["admin_user"])
