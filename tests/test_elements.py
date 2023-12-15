import sys

import pytest
from ttoolly.elements import common
from decimal import Decimal
import decimal
from datetime import timedelta


@pytest.mark.parametrize(
    "field_kwargs, expected_min, expected_max",
    [({}, -sys.maxsize - 1, sys.maxsize), ({"min_value": -5, "max_value": -5}, -5, -5)],
)
def test_int_get_random_value(field_kwargs, expected_min, expected_max):
    assert (
        expected_min
        <= common.FieldInt(**field_kwargs).get_random_value()
        <= expected_max
    )


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "max_value": 123,
                "min_value": -123,
                "only": {"if": "field2"},
                "unique": True,
                "lt": "field2",
                "lte": "field3",
                "step": 1,
            },
            {},
        ),
        ({"not_empty": False}, {}),
        ({"required": True}, {}),
        ({"required": {"if": "field"}}, {}),
        ({"required": {"if": {"field2": 3, "field3": 4}}}, {}),
        ({"required": {"if": {"field2": {}}}}, {}),
        ({"required": {"if": {"field2": []}}}, {}),
        ({"required": {"if": {"field2": None}}}, {}),
        ({"required": {"if": {"field2": "value"}}}, {}),
        ({"required": {"if": [{"field2": 3}, {"field3": 4}]}}, {}),
        ({"only": {"if": {"field2": {}}}}, {}),
        ({"only": {"if": {"field2": []}}}, {}),
        ({"only": {"if": {"field2": None}}}, {}),
        ({"only": {"if": {"field2": 3, "field3": "value"}}}, {}),
        ({"only": {"if": [{"field2": 3}, {"field3": 4}]}}, {}),
        ({"unique": False}, {}),
        ({"unique": {"with": ["field2", "field3"]}}, {}),
        ({"unique": {"case_sensitive": False}}, {}),
        ({"unique": {"case_sensitive": True}}, {}),
        ({"unique": {"with": ["field2", "field3"], "case_sensitive": False}}, {}),
        ({"lt": ["field1"]}, {}),
        ({"lte": ["field1", "field2"]}, {}),
    ],
)
def test_int_check_format(field_kwargs, expected):
    assert common.FieldInt(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"not_empty": "q"}, ValueError),
        ({"required": "q"}, ValueError),
        ({"required": {}}, ValueError),
        ({"required": {"if": 1}}, ValueError),
        ({"required": {"if": {}}}, ValueError),
        ({"required": {"if": []}}, ValueError),
        ({"required": {"if": [1]}}, ValueError),
        ({"required": {"if": ["value"]}}, ValueError),
        ({"required": {"if": [{}]}}, ValueError),
        ({"max_value": "qwe"}, ValueError),
        ({"max_value": 1.45}, ValueError),
        ({"min_value": "qwe"}, ValueError),
        ({"min_value": 1.45}, ValueError),
        ({"max_value": 1, "min_value": 2}, ValueError),
        ({"only": {"if": {}}}, ValueError),
        ({"only": {"if": []}}, ValueError),
        ({"only": {"if": [{}]}}, ValueError),
        ({"step": 1.4}, ValueError),
        ({"step": -2}, ValueError),
        ({"step": 4, 'min_value': 1, 'max_value': 4}, ValueError),
    ],
)
def test_int_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldInt(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, max_decimal_places, step, expected_min, expected_max",
    [
        (
            {},
            1,
            Decimal("0.1"),
            -Decimal(sys.float_info.max),
            Decimal(sys.float_info.max),
        ),
        (
            {"min_value": Decimal(1), "max_value": Decimal(1)},
            1,
            Decimal("0.1"),
            Decimal(1),
            Decimal(1),
        ),
        (
            {
                "min_value": Decimal(1),
                "max_value": Decimal(5),
                "step": Decimal("0.005"),
            },
            3,
            Decimal("0.005"),
            Decimal(1),
            Decimal(5),
        ),
        (
            {
                "min_value": Decimal(sys.float_info.max) - 1,
                "max_value": Decimal(sys.float_info.max),
            },
            1,
            Decimal("0.1"),
            Decimal(sys.float_info.max - 1),
            Decimal(sys.float_info.max),
        ),
    ],
)
def test_decimal_get_random_value(
    field_kwargs, max_decimal_places, step, expected_min, expected_max
):
    value = common.FieldDecimal(**field_kwargs).get_random_value()
    assert expected_min <= value <= expected_max
    assert len(str(value).split(".")[1]) == max_decimal_places
    with decimal.localcontext() as ctx:
        ctx.prec = 1000
        assert value % step == 0


@pytest.mark.parametrize(
    "field_class, expected",
    [
        (
            common.FieldBoolean,
            {
                "type": "bool",
                "only": None,
                "not_empty": True,
                "required": False,
                "unique": False,
            },
        ),
        (
            common.FieldChoice,
            {
                "type": "choice",
                "not_empty": False,
                "only": None,
                "required": False,
                "choice_values": [],
                "unique": False,
            },
        ),
        (
            common.FieldDate,
            {
                "type": "date",
                "lt": [],
                "lte": [],
                "min_value": None,
                "max_value": None,
                "not_empty": False,
                "only": None,
                "required": False,
                "step": timedelta(days=1),
                "unique": False,
            },
        ),
        (
            common.FieldDateTime,
            {
                "type": "datetime",
                "lt": [],
                "lte": [],
                "min_value": None,
                "max_value": None,
                "not_empty": False,
                "only": None,
                "required": False,
                "step": timedelta(seconds=1),
                "unique": False,
            },
        ),
        (
            common.FieldDecimal,
            {
                "type": "decimal",
                "lt": [],
                "lte": [],
                "max_value": Decimal(sys.float_info.max),
                "min_value": Decimal(-sys.float_info.max),
                "not_empty": False,
                "only": None,
                "required": False,
                "step": Decimal("0.1"),
                "max_decimal_places": 1,
                "unique": False,
            },
        ),
        (
            common.FieldFile,
            {
                "type": "file",
                "max_length": None,
                "min_length": 0,
                "null_allowed": True,
                "max_count": 1,
                "max_size": 10 * 1024 * 1024,
                "sum_max_size": 10 * 1024 * 1024,
                "extensions": (),
                "only": None,
                "not_empty": False,
                "required": False,
                "unique": False,
            },
        ),
        (
            common.FieldImage,
            {
                "type": "image",
                "max_length": None,
                "min_length": 0,
                "null_allowed": True,
                "max_count": 1,
                "max_size": 10 * 1024 * 1024,
                "sum_max_size": 10 * 1024 * 1024,
                "extensions": (),
                "min_height": 1,
                "max_height": 10000,
                "min_width": 1,
                "max_width": 10000,
                "only": None,
                "not_empty": False,
                "required": False,
                "unique": False,
            },
        ),
        (
            common.FieldInt,
            {
                "type": "int",
                "lt": [],
                "lte": [],
                "max_value": sys.maxsize,
                "min_value": -sys.maxsize - 1,
                "not_empty": False,
                "only": None,
                "required": False,
                "step": 1,
                "unique": False,
            },
        ),
        (
            common.FieldMultiselect,
            {
                "type": "multiselect",
                "not_empty": False,
                "only": None,
                "required": False,
                "choice_values": [],
                "unique": False,
            },
        ),
        (
            common.FieldSmallInt,
            {
                "type": "smallint",
                "lt": [],
                "lte": [],
                "max_value": 32767,
                "min_value": -32767 - 1,
                "not_empty": False,
                "only": None,
                "required": False,
                "step": 1,
                "unique": False,
            },
        ),
        (
            common.FieldStr,
            {
                "type": "str",
                "max_length": None,
                "min_length": 0,
                "not_empty": False,
                "null_allowed": True,
                "only": None,
                "required": False,
                "str_format": None,
                "unique": False,
            },
        ),
        (
            common.FieldTime,
            {
                "type": "time",
                "lt": [],
                "lte": [],
                "min_value": None,
                "max_value": None,
                "not_empty": False,
                "only": None,
                "required": False,
                "step": timedelta(seconds=1),
                "unique": False,
            },
        ),
        (
            common.FieldUuid,
            {
                "type": "uuid",
                "not_empty": False,
                "null_allowed": True,
                "only": None,
                "required": False,
                "unique": False,
            },
        ),
    ],
)
def test_get_template(field_class, expected):
    assert field_class().get_template() == expected
