import decimal
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

import pytest
from ttoolly.elements import common

from .assertions import assert_instance_fields
import re
from uuid import UUID

COMMON_CASES_POSITIVE = [
    (
        {"not_empty": False, "required": True},
        {
            "not_empty": False,
            "required": {"filled": None, "cases": []},
        },
    ),
    (
        {"required": True},
        {
            "required": {"filled": None, "cases": []},
            "not_empty": {"filled": None, "cases": []},
        },
    ),
    (
        {"required": {"if": "field"}},
        {"required": {"filled": "field", "cases": []}},
    ),
    (
        {"required": {"if": {"field2": 3, "field3": 4}}},
        {"required": {"filled": None, "cases": [{"field2": 3, "field3": 4}]}},
    ),
    (
        {"required": {"if": {"field2": {}}}},
        {"required": {"filled": None, "cases": [{"field2": {}}]}},
    ),
    (
        {"required": {"if": {"field2": []}}},
        {"required": {"filled": None, "cases": [{"field2": []}]}},
    ),
    (
        {"required": {"if": {"field2": None}}},
        {"required": {"filled": None, "cases": [{"field2": None}]}},
    ),
    (
        {"required": {"if": {"field2": "value"}}},
        {"required": {"filled": None, "cases": [{"field2": "value"}]}},
    ),
    (
        {"required": {"if": [{"field2": 3}, {"field3": 4}]}},
        {"required": {"filled": None, "cases": [{"field2": 3}, {"field3": 4}]}},
    ),
    (
        {"only": {"if": {"field2": {}}}},
        {"only": {"filled": None, "cases": [{"field2": {}}]}},
    ),
    (
        {"only": {"if": {"field2": []}}},
        {"only": {"filled": None, "cases": [{"field2": []}]}},
    ),
    (
        {"only": {"if": {"field2": None}}},
        {"only": {"filled": None, "cases": [{"field2": None}]}},
    ),
    (
        {"only": {"if": {"field2": 3, "field3": "value"}}},
        {"only": {"filled": None, "cases": [{"field2": 3, "field3": "value"}]}},
    ),
    (
        {"only": {"if": [{"field2": 3}, {"field3": 4}]}},
        {"only": {"filled": None, "cases": [{"field2": 3}, {"field3": 4}]}},
    ),
    ({"unique": False}, {"unique": False}),
    (
        {"unique": {"with": ["field2", "field3"]}},
        {"unique": {"case_sensitive": True, "with_fields": ["field2", "field3"]}},
    ),
    (
        {"unique": {"case_sensitive": False}},
        {"unique": {"case_sensitive": False, "with_fields": []}},
    ),
    (
        {"unique": {"case_sensitive": True}},
        {"unique": {"case_sensitive": True, "with_fields": []}},
    ),
    (
        {"unique": {"with": ["field2", "field3"], "case_sensitive": False}},
        {"unique": {"case_sensitive": False, "with_fields": ["field2", "field3"]}},
    ),
]

COMMON_CASES_NEGATIVE = [
    ({"not_empty": "q"}, ValueError),
    ({"required": "q"}, ValueError),
    ({"required": {}}, ValueError),
    ({"required": {"if": 1}}, ValueError),
    ({"required": {"if": {}}}, ValueError),
    ({"required": {"if": []}}, ValueError),
    ({"required": {"if": [1]}}, ValueError),
    ({"required": {"if": ["value"]}}, ValueError),
    ({"required": {"if": [{}]}}, ValueError),
    ({"required": {"other_field": ""}}, ValueError),
    ({"required": {"if": "qwe", "other_field": "qwe"}}, ValueError),
    ({"only": {"if": {}}}, ValueError),
    ({"only": {"if": []}}, ValueError),
    ({"only": {"if": [{}]}}, ValueError),
    ({"only": {"other_field": ""}}, ValueError),
    ({"only": {"if": "qwe", "other_field": "qwe"}}, ValueError),
    ({"unique": {"other_field": ""}}, ValueError),
    ({"unique": {"case_sensitive": False, "other_field": ""}}, ValueError),
    ({"unique": {"case_sensitive": "qwe"}}, ValueError),
    ({"unique": {"with": 123}}, ValueError),
    ({"unique": {"with": [123]}}, ValueError),
    ({"some_other_attr": 123}, AttributeError),
]


@pytest.mark.parametrize(
    "field_kwargs, expected_min, expected_max",
    [({}, -sys.maxsize - 1, sys.maxsize), ({"min_value": -5, "max_value": -5}, -5, -5)],
)
def test_int_get_random_value(field_kwargs, expected_min, expected_max):
    value = common.FieldInt(**field_kwargs).get_random_value()
    assert isinstance(value, int)
    assert expected_min <= value <= expected_max


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
            {
                "_form_type": None,
                "type_of": "int",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_value": 123,
                "min_value": -123,
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_value": sys.maxsize,
                "min_value": -sys.maxsize - 1,
            },
        ),
        ({"lt": ["field1"]}, {"lt": ["field1"]}),
        ({"lte": ["field1", "field2"]}, {"lte": ["field1", "field2"]}),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_int_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldInt(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_value": "qwe"}, ValueError),
        ({"max_value": 1.45}, ValueError),
        ({"min_value": "qwe"}, ValueError),
        ({"min_value": 1.45}, ValueError),
        ({"max_value": 1, "min_value": 2}, ValueError),
        ({"min_value": sys.maxsize + 1}, ValueError),
        ({"step": 1.4}, ValueError),
        ({"step": -2}, ValueError),
        ({"step": 4, "min_value": 1, "max_value": 4}, ValueError),
        ({"lt": ["field1", 123]}, ValueError),
        ({"lte": ["field1", 123]}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_int_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldInt(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected_min, expected_max",
    [({}, -32768, 32767), ({"min_value": -5, "max_value": -5}, -5, -5)],
)
def test_smallint_get_random_value(field_kwargs, expected_min, expected_max):
    assert (
        expected_min
        <= common.FieldSmallInt(**field_kwargs).get_random_value()
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
            {
                "_form_type": None,
                "type_of": "smallint",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_value": 123,
                "min_value": -123,
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_value": 32767,
                "min_value": -32768,
            },
        ),
        ({"lt": ["field1"]}, {"lt": ["field1"]}),
        ({"lte": ["field1", "field2"]}, {"lte": ["field1", "field2"]}),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_smallint_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldSmallInt(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_value": "qwe"}, ValueError),
        ({"max_value": 1.45}, ValueError),
        ({"min_value": "qwe"}, ValueError),
        ({"min_value": 1.45}, ValueError),
        ({"max_value": 1, "min_value": 2}, ValueError),
        ({"max_value": -32769}, ValueError),
        ({"step": 1.4}, ValueError),
        ({"step": -2}, ValueError),
        ({"step": 4, "min_value": 1, "max_value": 4}, ValueError),
        ({"lt": ["field1", 123]}, ValueError),
        ({"lte": ["field1", 123]}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_smallint_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldSmallInt(**field_kwargs)


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
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "max_value": "123.4",
                "min_value": -12,
                "only": {"if": "field2"},
                "unique": True,
                "lt": "field2",
                "lte": "field3",
                "step": "0.02",
                "max_decimal_places": 3,
            },
            {
                "_form_type": None,
                "type_of": "decimal",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_value": Decimal("123.4"),
                "min_value": Decimal("-12"),
                "step": Decimal("0.02"),
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_value": Decimal(sys.float_info.max),
                "min_value": Decimal(-sys.float_info.max),
            },
        ),
        ({"lt": ["field1"]}, {"lt": ["field1"]}),
        ({"lte": ["field1", "field2"]}, {"lte": ["field1", "field2"]}),
        ({"max_decimal_places": 2}, {"step": Decimal("0.01")}),
        (
            {"min_value": "-0.5", "max_value": "0.5", "step": "0.5"},
            {
                "min_value": Decimal("-0.5"),
                "max_value": Decimal("0.5"),
                "step": Decimal("0.5"),
            },
        ),
        (
            {"min_value": "-0.51", "max_value": "0.49", "step": "0.1"},
            {"max_decimal_places": 2},
        ),
        (
            {"min_value": "-0.5", "max_value": "0.5", "step": "0.001"},
            {"max_decimal_places": 3},
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_decimal_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldDecimal(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_value": "qwe"}, InvalidOperation),
        ({"min_value": "qwe"}, InvalidOperation),
        ({"max_value": 1, "min_value": 2}, ValueError),
        ({"step": -2}, ValueError),
        ({"step": 4, "min_value": 1, "max_value": 4}, ValueError),
        (
            {"step": "0.05", "max_decimal_places": 1},
            ValueError,
        ),
        (
            {"min_value": "1.234", "max_decimal_places": 2},
            ValueError,
        ),
        (
            {"max_value": "1.234", "max_decimal_places": 2},
            ValueError,
        ),
        (
            {"min_value": "-0.5", "max_value": "0.5", "step": "2"},
            ValueError,
        ),
        (
            {"min_value": "-0.5", "max_value": "0.5", "step": "0.3"},
            ValueError,
        ),
        ({"lt": ["field1", 123]}, ValueError),
        ({"lte": ["field1", 123]}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_decimal_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldDecimal(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected_min, expected_max",
    [
        (
            {},
            date.today().replace(day=1),
            date.today().replace(
                year=date.today().year + (1 if date.today().month == 12 else 0),
                month=date.today().month % 12 + 1,
                day=1,
            )
            - timedelta(days=1),
        ),
        (
            {"min_value": date.today() - timedelta(days=5)},
            date.today() - timedelta(days=5),
            date.today() + timedelta(days=-5 + 30),
        ),
        (
            {"max_value": date.today() + timedelta(days=5)},
            date.today() + timedelta(days=5 - 30),
            date.today() + timedelta(days=5),
        ),
        (
            {
                "min_value": date.today() - timedelta(days=1),
                "max_value": date.today() + timedelta(days=5),
            },
            date.today() - timedelta(days=1),
            date.today() + timedelta(days=5),
        ),
        (
            {
                "min_value": date.today() + timedelta(days=5),
                "max_value": date.today() + timedelta(days=5),
            },
            date.today() + timedelta(days=5),
            date.today() + timedelta(days=5),
        ),
    ],
)
def test_date_get_random_value(field_kwargs, expected_min, expected_max):
    value = common.FieldDate(**field_kwargs).get_random_value()
    assert isinstance(value, date)
    assert expected_min <= value <= expected_max


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "max_value": date.today() + timedelta(days=2),
                "min_value": date.today() - timedelta(days=4),
                "only": {"if": "field2"},
                "unique": True,
                "lt": "field2",
                "lte": "field3",
                "step": timedelta(days=3),
            },
            {
                "_form_type": None,
                "type_of": "date",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_value": date.today() + timedelta(days=2),
                "min_value": date.today() - timedelta(days=4),
                "step": timedelta(days=3),
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_value": None,
                "min_value": None,
                "step": timedelta(days=1),
            },
        ),
        ({"lt": ["field1"]}, {"lt": ["field1"]}),
        ({"lte": ["field1", "field2"]}, {"lte": ["field1", "field2"]}),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_date_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldDate(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_value": "qwe"}, ValueError),
        ({"max_value": 1}, ValueError),
        ({"min_value": "qwe"}, ValueError),
        ({"min_value": 1}, ValueError),
        (
            {"max_value": date.today(), "min_value": date.today() + timedelta(days=1)},
            ValueError,
        ),
        ({"step": 1}, ValueError),
        ({"step": timedelta(hours=1)}, ValueError),
        (
            {
                "step": timedelta(days=2),
                "min_value": date.today() - timedelta(days=2),
                "max_value": date.today() + timedelta(days=1),
            },
            ValueError,
        ),
        ({"lt": ["field1", 123]}, ValueError),
        ({"lte": ["field1", 123]}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_date_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldDate(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected_min, expected_max",
    [
        (
            {},
            datetime.today().replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            ),
            datetime.now().replace(
                year=datetime.now().year + (1 if datetime.now().month == 12 else 0),
                month=datetime.now().month % 12 + 1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            - timedelta(microseconds=1),
        ),
        (
            {"min_value": (now := datetime.now()) - timedelta(hours=5)},
            now - timedelta(hours=5),
            now + timedelta(hours=-5, days=30),
        ),
        (
            {"max_value": (now := datetime.now()) + timedelta(hours=15)},
            now + timedelta(hours=15, days=-30),
            now + timedelta(hours=15),
        ),
        (
            {
                "min_value": (now := datetime.now()) - timedelta(minutes=1),
                "max_value": now + timedelta(hours=2),
            },
            now - timedelta(minutes=1),
            now + timedelta(hours=2),
        ),
        (
            {
                "min_value": (now := datetime.now()) + timedelta(seconds=5),
                "max_value": now + timedelta(seconds=5),
            },
            now + timedelta(seconds=5),
            now + timedelta(seconds=5),
        ),
    ],
)
def test_datetime_get_random_value(field_kwargs, expected_min, expected_max):
    value = common.FieldDateTime(**field_kwargs).get_random_value()
    assert isinstance(value, datetime)
    assert expected_min <= value <= expected_max


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "max_value": (now := datetime.now()) + timedelta(days=2),
                "min_value": now - timedelta(days=4),
                "only": {"if": "field2"},
                "unique": True,
                "lt": "field2",
                "lte": "field3",
                "step": timedelta(minutes=3),
            },
            {
                "_form_type": None,
                "type_of": "datetime",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_value": now + timedelta(days=2),
                "min_value": now - timedelta(days=4),
                "step": timedelta(minutes=3),
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_value": None,
                "min_value": None,
                "step": timedelta(seconds=1),
            },
        ),
        ({"lt": ["field1"]}, {"lt": ["field1"]}),
        ({"lte": ["field1", "field2"]}, {"lte": ["field1", "field2"]}),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_datetime_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldDateTime(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_value": "qwe"}, ValueError),
        ({"max_value": 1}, ValueError),
        ({"min_value": "qwe"}, ValueError),
        ({"min_value": 1}, ValueError),
        (
            {
                "max_value": (now := datetime.now()),
                "min_value": now + timedelta(days=1),
            },
            ValueError,
        ),
        ({"step": 1}, ValueError),
        (
            {
                "step": timedelta(hours=5),
                "min_value": (now := datetime.now()) - timedelta(hours=2),
                "max_value": now + timedelta(hours=5),
            },
            ValueError,
        ),
        ({"lt": ["field1", 123]}, ValueError),
        ({"lte": ["field1", 123]}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_datetime_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldDateTime(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected_min, expected_max",
    [
        ({}, time(0, 0, 0, 0), time(23, 59, 59, 999999)),
        (
            {"min_value": time(12, 40, 30)},
            time(12, 40, 30),
            time(23, 59, 59, 999999),
        ),
        (
            {"max_value": time(0, 0, 0, 345678)},
            time(0, 0, 0),
            time(0, 0, 0, 345678),
        ),
        (
            {
                "min_value": time(0, 1, 10, 25),
                "max_value": time(0, 1, 15, 3034),
            },
            time(0, 1, 10, 25),
            time(0, 1, 15, 3034),
        ),
        (
            {
                "min_value": time(0, 1, 15, 3034),
                "max_value": time(0, 1, 15, 3034),
            },
            time(0, 1, 15, 3034),
            time(0, 1, 15, 3034),
        ),
    ],
)
def test_time_get_random_value(field_kwargs, expected_min, expected_max):
    value = common.FieldTime(**field_kwargs).get_random_value()
    assert isinstance(value, time)
    assert expected_min <= value <= expected_max


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "max_value": time(5, 45),
                "min_value": time(4, 15),
                "only": {"if": "field2"},
                "unique": True,
                "lt": "field2",
                "lte": "field3",
                "step": timedelta(minutes=3),
            },
            {
                "_form_type": None,
                "type_of": "time",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_value": time(5, 45),
                "min_value": time(4, 15),
                "step": timedelta(minutes=3),
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_value": time.max,
                "min_value": time.min,
                "step": timedelta(microseconds=1),
            },
        ),
        ({"lt": ["field1"]}, {"lt": ["field1"]}),
        ({"lte": ["field1", "field2"]}, {"lte": ["field1", "field2"]}),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_time_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldTime(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_value": "qwe"}, ValueError),
        ({"max_value": datetime.now()}, ValueError),
        ({"max_value": date.today()}, ValueError),
        ({"max_value": 1}, ValueError),
        ({"min_value": "qwe"}, ValueError),
        ({"min_value": datetime.now()}, ValueError),
        ({"min_value": date.today()}, ValueError),
        ({"min_value": 1}, ValueError),
        (
            {
                "max_value": time(10, 15),
                "min_value": time(10, 15, 30),
            },
            ValueError,
        ),
        ({"step": 1}, ValueError),
        ({"step": timedelta(days=1)}, ValueError),
        (
            {
                "step": timedelta(hours=5),
                "min_value": time(0, 15),
                "max_value": time(5, 16),
            },
            ValueError,
        ),
        ({"lt": ["field1", 123]}, ValueError),
        ({"lte": ["field1", 123]}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_time_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldTime(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected_re",
    [
        ({}, r"^.{1,100000}$"),
        ({"min_length": 5, "max_length": 10}, r"^.{5,10}$"),
        ({"str_format": "email"}, r"^.{1,64}@.+$"),
        ({"str_format": {"re": r"\d{2}-\w{5}"}}, r"^\d{2}-\w{5}$"),
    ],
)
def test_str_get_random_value(field_kwargs, expected_re):
    value = common.FieldStr(**field_kwargs).get_random_value()
    assert isinstance(value, str)
    assert re.match(expected_re, value)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "max_length": 20,
                "min_length": 5,
                "only": {"if": "field2"},
                "unique": True,
                "str_format": "email",
                "null_allowed": False,
            },
            {
                "_form_type": None,
                "type_of": "str",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_length": 20,
                "min_length": 5,
                "str_format": "email",
                "null_allowed": False,
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_length": None,
                "min_length": 0,
                "null_allowed": True,
                "str_format": None,
            },
        ),
        ({"str_format": "email_simple"}, {"str_format": "email_simple"}),
        ({"str_format": {"re": r"\d+"}}, {"str_format": {"re": r"\d+"}}),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_str_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldStr(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"min_length": "qwe"}, ValueError),
        ({"min_length": -1}, ValueError),
        ({"max_length": "qwe"}, ValueError),
        ({"max_length": 10, "min_length": 11}, ValueError),
        ({"str_format": "qwe"}, ValueError),
        ({"str_format": {}}, ValueError),
        ({"str_format": {"qwe": "123"}}, ValueError),
        ({"str_format": {"re": ""}}, ValueError),
        ({"str_format": {"re": 123}}, TypeError),
        ({"str_format": {"re": "**"}}, re.error),
        ({"null_allowed": "qwe"}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_str_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldStr(**field_kwargs)


def test_uuid_get_random_value():
    value = common.FieldUuid().get_random_value()
    assert isinstance(value, UUID)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "only": {"if": "field2"},
                "unique": True,
                "null_allowed": False,
            },
            {
                "_form_type": None,
                "type_of": "uuid",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "null_allowed": False,
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "null_allowed": True,
            },
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_uuid_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldUuid(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"null_allowed": "qwe"}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_uuid_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldUuid(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "only": {"if": "field2"},
                "unique": True,
                "choice_values": [1, 2, 3],
            },
            {
                "_form_type": None,
                "type_of": "select",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "choice_values": [1, 2, 3],
            },
        ),
        (
            {"not_empty": False, "choice_values": ["a"]},
            {"not_empty": False, "choice_values": ["a"]},
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_select_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldSelect(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    COMMON_CASES_NEGATIVE,
)
def test_select_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldSelect(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "only": {"if": "field2"},
                "unique": True,
                "choice_values": [1, 2, 3],
            },
            {
                "_form_type": None,
                "type_of": "multiselect",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "choice_values": [1, 2, 3],
            },
        ),
        (
            {"not_empty": False, "choice_values": ["a"]},
            {"not_empty": False, "choice_values": ["a"]},
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_multiselect_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldMultiselect(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    COMMON_CASES_NEGATIVE,
)
def test_multiselect_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldMultiselect(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "only": {"if": "field2"},
                "unique": True,
                "max_length": 100,
                "min_length": 10,
                "null_allowed": False,
                "max_count": 5,
                "max_size": 1024,
                "sum_max_size": 4096,
                "extensions": ("txt", "pdf"),
            },
            {
                "_form_type": None,
                "type_of": "file",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_length": 100,
                "min_length": 10,
                "null_allowed": False,
                "max_count": 5,
                "max_size": 1024,
                "sum_max_size": 4096,
                "extensions": ("txt", "pdf"),
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_length": None,
                "min_length": 0,
                "null_allowed": True,
                "max_count": 1,
                "max_size": 10 * 1024 * 1024,
                "sum_max_size": 10 * 1024 * 1024,
                "extensions": (),
            },
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_file_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldFile(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_length": "qwe"}, ValueError),
        ({"min_length": "qwe"}, ValueError),
        ({"min_length": 100, "max_length": 99}, ValueError),
        ({"null_allowed": "qwe"}, ValueError),
        ({"max_count": 0}, ValueError),
        ({"max_count": "qwe"}, ValueError),
        ({"max_size": 0}, ValueError),
        ({"max_size": "qwe"}, ValueError),
        ({"sum_max_size": 0}, ValueError),
        ({"sum_max_size": "qwe"}, ValueError),
        ({"sum_max_size": 100, "max_size": 101}, ValueError),
        ({"extensions": 123}, TypeError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_file_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldFile(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "only": {"if": "field2"},
                "unique": True,
                "max_length": 100,
                "min_length": 10,
                "null_allowed": False,
                "max_count": 5,
                "max_size": 1024,
                "sum_max_size": 4096,
                "extensions": ("jpg", "svg"),
                "min_width": 100,
                "min_height": 60,
                "max_width": 2000,
                "max_height": 1000,
            },
            {
                "_form_type": None,
                "type_of": "image",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
                "max_length": 100,
                "min_length": 10,
                "null_allowed": False,
                "max_count": 5,
                "max_size": 1024,
                "sum_max_size": 4096,
                "extensions": ("jpg", "svg"),
                "min_width": 100,
                "min_height": 60,
                "max_width": 2000,
                "max_height": 1000,
            },
        ),
        (
            {"not_empty": False},
            {
                "not_empty": False,
                "max_length": None,
                "min_length": 0,
                "null_allowed": True,
                "max_count": 1,
                "max_size": 10 * 1024 * 1024,
                "sum_max_size": 10 * 1024 * 1024,
                "extensions": (),
                "min_width": 1,
                "min_height": 1,
                "max_width": 10000,
                "max_height": 10000,
            },
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_image_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldImage(**field_kwargs), expected)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    [
        ({"max_length": "qwe"}, ValueError),
        ({"min_length": "qwe"}, ValueError),
        ({"min_length": 100, "max_length": 99}, ValueError),
        ({"null_allowed": "qwe"}, ValueError),
        ({"max_count": 0}, ValueError),
        ({"max_count": "qwe"}, ValueError),
        ({"max_size": 0}, ValueError),
        ({"max_size": "qwe"}, ValueError),
        ({"sum_max_size": 0}, ValueError),
        ({"sum_max_size": "qwe"}, ValueError),
        ({"sum_max_size": 100, "max_size": 101}, ValueError),
        ({"extensions": 123}, TypeError),
        ({"extensions": ("txt",)}, ValueError),
        ({"min_width": 0}, ValueError),
        ({"min_width": "qwe"}, ValueError),
        ({"min_height": 0}, ValueError),
        ({"min_height": "qwe"}, ValueError),
        ({"max_width": 0}, ValueError),
        ({"max_width": "qwe"}, ValueError),
        ({"max_height": 0}, ValueError),
        ({"max_height": "qwe"}, ValueError),
        ({"min_width": 100, "max_width": 99}, ValueError),
        ({"min_height": 100, "max_height": 99}, ValueError),
    ]
    + COMMON_CASES_NEGATIVE,
)
def test_image_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldImage(**field_kwargs)


@pytest.mark.parametrize(
    "field_kwargs, expected",
    [
        (
            {
                "not_empty": True,
                "required": False,
                "only": {"if": "field2"},
                "unique": True,
            },
            {
                "_form_type": None,
                "type_of": "bool",
                "unique": {"case_sensitive": True, "with_fields": []},
                "not_empty": {"filled": None, "cases": []},
                "required": False,
                "only": {"filled": "field2", "cases": []},
            },
        ),
        (
            {"not_empty": False},
            {"not_empty": False},
        ),
    ]
    + COMMON_CASES_POSITIVE,
)
def test_boolean_check_format(field_kwargs, expected):
    assert_instance_fields(common.FieldBoolean(**field_kwargs), expected)


def test_boolean_get_random_value():
    value = common.FieldBoolean().get_random_value()
    assert isinstance(value, bool)


@pytest.mark.parametrize(
    "field_kwargs, exc",
    COMMON_CASES_NEGATIVE,
)
def test_boolean_check_format_with_error(field_kwargs, exc):
    with pytest.raises(exc):
        common.FieldBoolean(**field_kwargs)


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
            common.FieldSelect,
            {
                "type": "select",
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
                "min_value": time.min,
                "max_value": time.max,
                "not_empty": False,
                "only": None,
                "required": False,
                "step": timedelta(microseconds=1),
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
    assert field_class.get_template() == expected
