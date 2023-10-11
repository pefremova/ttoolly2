import decimal
import inspect
import math
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import cached_property
from random import choice, randint, uniform
from collections.abc import Iterable, Iterator
from types import UnionType
from uuid import uuid4

from faker import Faker
from ttoolly.utils import (
    convert_size_to_bytes,
    get_all_subclasses,
    get_randname,
    get_random_email_value,
)

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

    @classmethod
    def validate(self, **kwargs):
        message = (
            "Use one of the following formats:"
            '\n{"if": "field_name"}'
            '\n{"if": {"field_name": "value"}}'
            '\n{"if": [{"field_name": "value_1"}, {"other_field_name": "value_2"}]'
        )
        if not "if" in kwargs.keys():
            raise ValueError(message)
        if not isinstance(kwargs["if"], (str, dict, list)):
            raise ValueError(message)
        if isinstance(kwargs["if"], list) and not all(
            [isinstance(el, dict) for el in kwargs["if"]]
        ):
            raise ValueError(message)


class Unique:
    value: bool = False
    case_sensitive: bool = True
    with_fields = []


class Choices:
    cases = []  # Condition + values


class Field:
    _form_type = None
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

    @classmethod
    def validate(cls, **kwargs):
        type_of = kwargs.pop("type", None)
        real_attrs = []
        for k, v in inspect.getmembers(cls):
            if not (k.startswith("_") or inspect.ismethod(v) or inspect.isfunction(v)):
                real_attrs.append(k)

        def get_annotations(cls):
            res = {}
            for bcs in cls.__bases__:
                res.update(get_annotations(bcs))
            res.update(getattr(cls, "__annotations__", {}))
            return res

        annotations = get_annotations(cls)

        def check_by_type(v, tt):
            if not isinstance(tt, UnionType) and Iterable in tt.mro():
                isinstance(v, Iterable)
                if hasattr(tt, "__args__"):
                    for vv in v:
                        isinstance(vv, tt.__args__)
                return True

            if isinstance(v, tt):
                return True
            for t in tt.__args__:
                if hasattr(t, "validate"):
                    t.validate(**v)
                    return True
            raise ValueError(
                f'Type of attribute "{k}" value ({v}) must be {annotations[k]}'
            )

        for k, v in kwargs.items():
            if k not in real_attrs:
                raise AttributeError(f"Unknown attribute {k} for type {type_of} {cls}")
            check_by_type(v, annotations[k])


class FieldInt(Field):
    type_of = "int"
    max_value: int = sys.maxsize
    min_value: int = -sys.maxsize - 1
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
    min_value: Decimal = Decimal(-sys.float_info.max)
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: Decimal = Decimal("0.1")
    max_decimal_places: int = 1

    def __init__(self, **kwargs):
        for field in ("max_value", "min_value", "step"):
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

            if kwargs["step"] == int(kwargs["step"]):
                step_decimal_places = 0
            else:
                step_decimal_places = len(str(kwargs["step"]).split(".")[1])
            if step_decimal_places != kwargs["max_decimal_places"]:
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
        if not isinstance(self.str_format, dict) and not self.min_length:
            self.min_length = {"email": 3, "email_simple": 3}.get(self.str_format, 0)

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
    _form_type = None

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

    @cached_property
    def _field_classes_according_to_form_type(self):
        data = {"group": self.__class__}
        for el in get_all_subclasses(Field):
            if data.get(el.type_of):
                if el._form_type == self._form_type:
                    data[el.type_of] = el
            elif el._form_type in (self._form_type, None):
                data[el.type_of] = el
        return data

    def __init__(self, **kwargs):
        self.Meta.all_fields = set()
        for field_name, data in kwargs.pop("fields").items():
            field_class = self._field_classes_according_to_form_type.get(
                data["type"], Field
            )
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
