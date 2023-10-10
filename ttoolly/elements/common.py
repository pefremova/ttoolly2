from collections.abc import Iterable, Iterator
from datetime import timedelta, date, datetime, time
from random import randint, uniform, choice
from decimal import Decimal
import math
from ttoolly.utils import (
    convert_size_to_bytes,
    get_randname,
    get_all_subclasses,
    get_random_email_value,
)
import sys
import inspect
from uuid import uuid4
from faker import Faker
import decimal


fake = Faker()


class Condition:
    filled: str | None = None
    cases: Iterable[str | dict | Iterator] = []

    def __init__(self, data):
        if isinstance(data, bool):
            return
        data = data["if"]
        if isinstance(data, str):
            self.filled = data
            return
        if isinstance(data, dict):
            data = [data]
        self.cases = data

    def has_condition(self):
        if self.filled or self.cases:
            return True
        return False


class Unique:
    value: bool = False
    case_sensitive: bool = True
    with_fields = []


class Choices:
    cases = []  # Condition + values


class Field:
    name: str = None
    type_of: str
    not_empty: bool = False
    required: Condition | bool = False
    only: Condition | None = None
    unique: Unique | bool = False

    def __init__(self, **kwargs):
        self.validate(**kwargs)
        if required := kwargs.pop("required", None):
            self.required = Condition(required)
        if only := kwargs.pop("only", None):
            self.only = Condition(only)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def get_template(cls):
        result = {}
        for k, v in inspect.getmembers(cls):
            if not (
                k.startswith("_")
                or k in ("name",)
                or inspect.ismethod(v)
                or inspect.isfunction(v)
            ):
                result[{"type_of": "type"}.get(k, k)] = v
        return result

    def validate(self, **kwargs):
        type_of = kwargs.pop("type", None)
        real_attrs = []
        for k, v in inspect.getmembers(self):
            if not (k.startswith("_") or inspect.ismethod(v) or inspect.isfunction(v)):
                real_attrs.append(k)

        def get_annotations(cls):
            res = {}
            for bcs in cls.__bases__:
                res.update(get_annotations(bcs))
            res.update(getattr(cls, "__annotations__", {}))
            return res

        for k, v in kwargs.items():
            if k not in real_attrs:
                raise Exception(
                    f"Unknown attribute {k} for type {type_of} {self.__class__}"
                )
            # TODO: validate type


class FieldInt(Field):
    type_of = "int"
    max_value = sys.maxsize
    min_value = -sys.maxsize - 1
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: int = 1

    def get_random_value(self) -> int:
        value = randint(self.min_value, self.max_value)
        value = value - value % self.step
        return value


class FieldSmallInt(FieldInt):
    type_of = "smallint"
    max_value: int = 32767
    min_value: int = -32767 - 1


class FieldDecimal(Field):
    type_of = "decimal"
    max_value: Decimal = Decimal(sys.float_info.max)
    min_value = Decimal(-sys.float_info.max)
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: Decimal = Decimal("0.1")
    max_decimal_places: int = 1

    def __init__(self, **kwargs):
        for field in ("max_value", "min_value"):
            if field in kwargs.keys():
                kwargs[field] = Decimal(kwargs[field])
        super().__init__(**kwargs)
        if "step" in kwargs.keys() and "max_decimal_places" not in kwargs.keys():
            self.max_decimal_places = int(math.log(self.step, Decimal("0.1")))
        elif "max_decimal_places" in kwargs.keys() and "step" not in kwargs.keys():
            self.step = Decimal("0.1") ** kwargs["max_decimal_places"]

    def get_random_value(self) -> Decimal:
        if self.min_value < 0 and self.max_value > 0:
            """For big numbers, like sys.float_info.max"""
            if randint(0, 1):
                value = uniform(0, float(self.max_value))
            else:
                value = uniform(float(self.min_value), 0)
        else:
            value = uniform(float(self.min_value), float(self.max_value))
        value = Decimal(value)
        with decimal.localcontext() as ctx:
            ctx.prec = 1000
            value = value - value % self.step
            value = value.quantize(self.step)

        return value

    def validate(self, **kwargs):
        super().validate(**kwargs)
        if "step" in kwargs.keys() and "max_decimal_places" in kwargs.keys():
            expected_step = Decimal("0.1") ** kwargs["max_decimal_places"]
            if len(str(kwargs["step"]).split(".")[1]) != kwargs["max_decimal_places"]:
                raise Exception(
                    f"With max_decimal_places {kwargs['max_decimal_places']} step couldn't be {kwargs['step']}. Maybe {expected_step}?"
                )


class FieldDate(Field):
    type_of = "date"
    max_value: date | None = None
    min_value: date | None = None
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: timedelta = timedelta(days=1)

    def get_random_value(self):
        if self.max_value and self.min_value:
            return fake.date_between_dates(self.min_value, self.max_value)
        if self.max_value:
            return fake.date_between_dates(
                self.max_value - timedelta(days=30), self.max_value
            )
        if self.min_value:
            return fake.date_between_dates(
                self.min_value, self.min_value + timedelta(days=30)
            )
        return fake.date_this_month()


class FieldDateTime(Field):
    type_of = "datetime"
    max_value: datetime | None = None
    min_value: datetime | None = None
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: timedelta = timedelta(seconds=1)

    def get_random_value(self):
        if self.max_value and self.min_value:
            return fake.date_time_between_dates(self.min_value, self.max_value)
        if self.max_value:
            return fake.date_time_between_dates(
                self.max_value - timedelta(days=30), self.max_value
            )
        if self.min_value:
            return fake.date_time_between_dates(
                self.min_value, self.min_value + timedelta(days=30)
            )
        return fake.date_time_this_month()


class FieldTime(Field):
    type_of = "time"
    max_value: time | None = None
    min_value: time | None = None
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: timedelta = timedelta(seconds=1)

    def get_random_value(self):
        # TODO
        return fake.time_object()


class FieldStr(Field):
    type_of = "str"
    max_length: int | None = None
    min_length: int = 0
    str_format: dict | str | None = None
    null_allowed: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(self.str_format, dict) and not self.max_length:
            self.max_length = {"email": 254, "email_simple": 254}.get(
                self.str_format, None
            )

    def get_random_value(self, length=None):
        length = (
            length
            if length is not None
            else randint(self.min_length or 1, self.max_length or 100000)
        )

        if isinstance(self.str_format, dict):
            raise Exception("TODO")
        elif self.str_format:
            fun = {
                "email": get_random_email_value,
                "email_simple": get_random_email_value,
            }[self.str_format]
            kwargs = {}
            if self.str_format == "email_simple":
                kwargs = {"safe": True}
            return fun(length, **kwargs)

        return get_randname(length, "w")


class FieldUuid(Field):
    type_of = "uuid"
    null_allowed: bool = True

    def get_random_value(self, *a, **k):
        return uuid4()


class FieldChoice(Field):
    type_of = "choice"
    choice_values: Iterable = []

    def get_random_value(self, *a, **k):
        # TODO
        return choice(self.choice_values)


class FieldMultiselect(FieldChoice):
    type_of = "multiselect"

    def get_random_value(self, *a, **k):
        # TODO
        return [choice(self.choice_values)]


class FieldFile(Field):
    type_of = "file"
    max_length: int | None = None
    min_length: int = 0
    null_allowed: bool = True
    max_count: int = 1
    max_size: int = 10 * 1024 * 1024  # 10M
    sum_max_size: int = 10 * 1024 * 1024  # 10M
    extensions: Iterable[str] = ()

    def __init__(self, **kwargs):
        for field in ("max_size", "sum_max_size"):
            if field in kwargs.keys():
                kwargs[field] = convert_size_to_bytes(kwargs[field])
        super().__init__(**kwargs)


class FieldImage(FieldFile):
    type_of = "image"
    min_width: int = 1
    min_height: int = 1
    max_width: int = 10000
    max_height: int = 10000


class FieldBoolean(Field):
    type_of = "bool"
    not_empty: bool = True

    def get_random_value(self):
        return choice((True, False))


class Form:
    class Meta:
        max_count: int = 1
        min_count: int = 0
        name_format = "{field}"
        all_fields = None

    def __getitem__(self, k, *a):
        return getattr(self, k)

    def __setitem__(self, k, v):
        self.Meta.all_fields.update((k,))
        setattr(self, k, v)

    def __init__(self, **kwargs):
        self.Meta.all_fields = set()
        for field_name, data in kwargs.pop("fields").items():
            field_class = (
                {"group": Form} | {el.type_of: el for el in get_all_subclasses(Field)}
            ).get(data["type"], Field)
            data["name"] = field_name
            self[field_name] = field_class(**data)
        for k, v in kwargs.items():
            setattr(self.Meta, k, v)

    def get_one_of_fields(self):
        """
        Groups of fields which cannot be filled together
        """
        all_fields_names = self.Meta.all_fields
        result = {}
        for name in all_fields_names:
            field = self[name]
            _result = []
            if field.only and field.only.cases:
                for data in field.only.cases:
                    one_group_fields = []
                    for k, v in data.items():
                        if not v:
                            one_group_fields.append(k)
                    if one_group_fields:
                        _result.append(one_group_fields)
            result[name] = _result
        return result

    def get_required_fields(self) -> Iterator[str]:
        # FIXME: for related fields
        all_fields_names = self.Meta.all_fields
        result = []
        for name in all_fields_names:
            if self[name].required:
                result.append(name)
        return result

    def get_random_data(
        self, fields: Iterable[str] | None = None, additional: dict | None = None
    ) -> dict:
        if fields is None:
            fields = self.get_required_fields()
        data = {f: self[f].get_random_value() for f in fields}
        data.update(additional or {})
        return data
