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
