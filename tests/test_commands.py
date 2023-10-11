from pprint import pformat
from ttoolly.elements.common import FieldStr


def test_get_field_template(script_runner):
    result = script_runner.run(["tt_get_field_template", "f1:str"])
    assert result.stdout.strip() == pformat({"f1": FieldStr().get_template()})


def test_get_field_template_wrong_format(script_runner):
    result = script_runner.run(["tt_get_field_template", "f1 str"])
    assert 'Wrong format "f1 str". Should be <field name>:<field type>' in result.stderr


def test_get_field_template_unknown_type(script_runner):
    result = script_runner.run(["tt_get_field_template", "f1:some_wrong_type"])
    assert 'Unexpected field type: "some_wrong_type"' in result.stderr
