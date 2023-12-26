import decimal
import inspect
import math
import sys
from collections.abc import Iterable, Iterator
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import cached_property
from random import choice, randint, uniform
from types import UnionType
from uuid import uuid4

import rstr
from faker import Faker
from ttoolly.utils import convert_size_to_bytes, get_all_subclasses, randomizer
import re

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
    def validate(cls, **kwargs):
        message = (
            "Use one of the following formats:"
            '\n{"if": "field_name"}'
            '\n{"if": {"field_name": "value"}}'
            '\n{"if": [{"field_name": "value_1"}, {"other_field_name": "value_2"}]'
        )
        if ["if"] != list(kwargs.keys()):
            raise ValueError(message)
        if not isinstance(kwargs["if"], (str, dict, list)):
            raise ValueError(message)
        if not kwargs["if"]:
            raise ValueError("Condition can not be empty\n" + message)
        if isinstance(kwargs["if"], list):
            if not all([isinstance(el, dict) for el in kwargs["if"]]):
                raise ValueError(message)
            if not all(kwargs["if"]):
                raise ValueError("Condition can not be empty\n" + message)


class Unique:
    case_sensitive: bool = True
    with_fields: Iterable[str] = []

    def __init__(self, data):
        if isinstance(data, bool):
            return
        self.with_fields = data.get('with', [])
        self.case_sensitive = data.get('case_sensitive', True)

    @classmethod
    def validate(cls, **kwargs):
        message = (
            "Use one of the following formats:"
            '\n{"with": ["field_name"]}'
            '\n{"case_sensetive": False}'
            '\n{"with": ["field_name"], "case_sensetive": False}'
        )
        if not set(kwargs.keys()).intersection(("with", "case_sensitive")):
            raise ValueError(message)
        if set(kwargs.keys()).difference(("with", "case_sensitive")):
            raise ValueError(message)
        if not isinstance(kwargs.get("case_sensitive", False), bool):
            raise ValueError(message)
        if with_fields := kwargs.get("with", []):
            if not isinstance(with_fields, list):
                raise ValueError(message)
            if not all([isinstance(el, str) for el in with_fields]):
                raise ValueError(message)


class Choices:
    cases = []  # Condition + values


class Field:
    _form_type = None
    name: str = None
    type_of: str
    not_empty: Condition | bool = False
    required: Condition | bool = False
    only: Condition | None = None
    unique: Unique | bool = False

    def __init__(self, **kwargs):
        self.validate(**kwargs)
        if required := kwargs.pop("required", None):
            self.required = Condition(required)
        if (not_empty := kwargs.pop("not_empty", None)) is None:
            # TODO: usually different behavior of api and form-based
            self.not_empty = self.required
        elif not_empty:
            self.not_empty = Condition(not_empty)
        else:
            self.not_empty = False
        if only := kwargs.pop("only", None):
            self.only = Condition(only)
        if unique := kwargs.pop("unique", None):
            self.unique = Unique(unique)
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
                if hasattr(tt, "__args__"):
                    for vv in v:
                        if not isinstance(vv, tt.__args__):
                            raise ValueError(
                                f'Type of value "{vv}" must be {tt.__args__}'
                            )
                return

            if isinstance(v, tt):
                return
            for t in getattr(tt, "__args__", ()):
                if hasattr(t, "validate"):
                    if not isinstance(v, dict):
                        raise ValueError(f'Type of value "{v}" must be dict')
                    t.validate(**v)
                    return
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

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)
        max_value = kwargs.get('max_value', cls.max_value)
        min_value = kwargs.get('min_value', cls.min_value)
        step = kwargs.get('step', cls.step)
        if max_value < min_value:
            raise ValueError(
                f'Max_value ({max_value}) can not be less than min_value ({min_value})'
            )
        if step < 1:
            raise ValueError(f'Step must be positive int. Now {step}')
        if (max_value - min_value) > 0:
            if (max_value - min_value) % step > 0:
                raise ValueError(
                    f'Difference between min_value ({min_value}) and max_value ({max_value}) must be divided by step ({step}) without reminder'
                )


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
            self.max_decimal_places = max(
                [
                    len(
                        str(
                            kwargs[field_name] % int(kwargs[field_name])
                            if abs(kwargs[field_name]) > 1
                            else kwargs[field_name]
                        ).split(".")[1]
                    )
                    if int(kwargs[field_name]) != kwargs[field_name]
                    else 0
                    for field_name in ("max_value", "min_value", "step")
                ]
            )
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

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)

        if "max_decimal_places" in kwargs.keys():
            expected_step = Decimal("0.1") ** kwargs["max_decimal_places"]
            for field_name in ("max_value", "min_value", "step"):
                if field_name in kwargs.keys():
                    value_decimal_places = (
                        len(
                            str(
                                kwargs[field_name] % int(kwargs[field_name])
                                if abs(kwargs[field_name]) > 1
                                else kwargs[field_name]
                            ).split(".")[1]
                        )
                        if int(kwargs[field_name]) != kwargs[field_name]
                        else 0
                    )
                    if value_decimal_places > kwargs["max_decimal_places"]:
                        raise ValueError(
                            f"With max_decimal_places {kwargs['max_decimal_places']} {field_name} couldn't be {kwargs[field_name]}. Maybe {expected_step}?"
                        )

        max_value = kwargs.get('max_value', cls.max_value)
        min_value = kwargs.get('min_value', cls.min_value)
        step = kwargs.get('step', cls.step)
        if max_value < min_value:
            raise ValueError(
                f'Max_value ({max_value}) can not be less than min_value ({min_value})'
            )
        if step < 0:
            raise ValueError(f'Step must be positive. Now {step}')
        if (max_value - min_value) > 0:
            with decimal.localcontext() as ctx:
                ctx.prec = 1000
                if (max_value - min_value) % step > 0:
                    raise ValueError(
                        f'Difference between min_value ({min_value}) and max_value ({max_value}) must be divided by step ({step}) without reminder'
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

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)
        max_value = kwargs.get('max_value')
        min_value = kwargs.get('min_value')
        step = kwargs.get('step', cls.step)
        if step < timedelta(days=1):
            raise ValueError(f'Step must be great than or equal 1 day. Now {step}')
        if max_value and min_value:
            if max_value < min_value:
                raise ValueError(
                    f'Max_value ({max_value}) can not be less than min_value ({min_value})'
                )
            if (max_value - min_value) >= timedelta(days=1):
                if (max_value - min_value) % step > timedelta():
                    raise ValueError(
                        f'Difference between min_value ({min_value}) and max_value ({max_value}) must be divided by step ({step}) without reminder'
                    )


class FieldDateTime(Field):
    type_of = "datetime"
    max_value: datetime | None = None
    min_value: datetime | None = None
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: timedelta = timedelta(seconds=1)

    def get_random_value(self):
        if self.max_value and self.min_value:
            return randomizer.get_random_datetime_value(self.min_value, self.max_value)
        if self.max_value:
            return randomizer.get_random_datetime_value(
                self.max_value - timedelta(days=30), self.max_value
            )
        if self.min_value:
            return randomizer.get_random_datetime_value(
                self.min_value, self.min_value + timedelta(days=30)
            )
        return randomizer.get_random_datetime_value()

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)
        max_value = kwargs.get('max_value')
        min_value = kwargs.get('min_value')
        step = kwargs.get('step', cls.step)
        if max_value and min_value:
            if max_value < min_value:
                raise ValueError(
                    f'Max_value ({max_value}) can not be less than min_value ({min_value})'
                )
            if (max_value - min_value) > timedelta():
                if (max_value - min_value) % step > timedelta():
                    raise ValueError(
                        f'Difference between min_value ({min_value}) and max_value ({max_value}) must be divided by step ({step}) without reminder'
                    )


class FieldTime(Field):
    type_of = "time"
    max_value: time = time.max
    min_value: time = time.min
    lt: Iterable[str] = []
    lte: Iterable[str] = []
    step: timedelta = timedelta(microseconds=1)

    def get_random_value(self):
        return randomizer.get_random_datetime_value(
            datetime.combine(date.today(), self.min_value),
            datetime.combine(date.today(), self.max_value),
        ).time()

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)
        max_value = kwargs.get('max_value', cls.max_value)
        min_value = kwargs.get('min_value', cls.min_value)
        step = kwargs.get('step', cls.step)
        if step >= timedelta(days=1):
            raise ValueError(f'Step ({step}) must be less than 1 day')
        if max_value < min_value:
            raise ValueError(
                f'Max_value ({max_value}) can not be less than min_value ({min_value})'
            )
        today = date.today()
        if (
            difference := datetime.combine(today, max_value)
            - datetime.combine(today, min_value)
        ) > timedelta():
            if difference % step > timedelta():
                raise ValueError(
                    f'Difference between min_value ({min_value}) and max_value ({max_value}) must be divided by step ({step}) without reminder'
                )


class FieldStr(Field):
    type_of = "str"
    max_length: int | None = None
    min_length: int = 0
    str_format: dict | str | None = None
    null_allowed: bool = True
    __available_str_formats = ("email", "email_simple")

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
            return rstr.xeger(self.str_format["re"])
        elif self.str_format:
            fun = {
                "email": randomizer.get_random_email_value,
                "email_simple": randomizer.get_random_email_value,
            }[self.str_format]
            kwargs = {}
            if self.str_format == "email_simple":
                kwargs = {"safe": True}
            return fun(length, **kwargs)
        return randomizer.get_randname(length, "w")

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)
        if kwargs.get("min_length") and kwargs["min_length"] < 0:
            raise ValueError(
                f"Min_length ({kwargs['min_length']}) can not be less than 0"
            )
        if kwargs.get("max_length") and kwargs["max_length"] < kwargs.get(
            "min_length", cls.min_length
        ):
            raise ValueError(
                f"Max_length ({kwargs['max_length']}) can not be less than min_length ({kwargs.get('min_length', cls.min_length)})"
            )
        if (str_format := kwargs.get("str_format")) is not None:
            if (
                isinstance(str_format, str)
                and str_format not in cls.__available_str_formats
            ):
                raise ValueError(
                    f"Available values for str_format ({str_format}): {', '.join(cls.__available_str_formats)}"
                )
            elif isinstance(str_format, dict):
                if not list(str_format.keys()) == ["re"]:
                    raise ValueError(
                        f"Available format for str_format ({str_format}): {{\"re\": <regex>}}"
                    )
                if not str_format["re"]:
                    raise ValueError(f"Regexp in str_format can not be empty")
                re.compile(str_format["re"])


class FieldUuid(Field):
    type_of = "uuid"
    null_allowed: bool = True

    def get_random_value(self, *a, **k):
        return uuid4()


class FieldSelect(Field):
    type_of = "select"
    choice_values: Iterable = []  # TODO

    def get_random_value(self, *a, **k):
        # TODO
        return choice(self.choice_values)


class FieldMultiselect(FieldSelect):
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
        super().__init__(**kwargs)
        for field in ("max_size", "sum_max_size"):
            if field in kwargs.keys():
                kwargs[field] = convert_size_to_bytes(kwargs[field])

    @classmethod
    def validate(cls, **kwargs):
        super().validate(**kwargs)
        if "min_length" in kwargs.keys() and kwargs["min_length"] < 0:
            raise ValueError(
                f"Min_length ({kwargs['min_length']}) can not be less than 0"
            )
        if "max_length" in kwargs.keys() and kwargs["max_length"] < kwargs.get(
            "min_length", cls.min_length
        ):
            raise ValueError(
                f"Max_length ({kwargs['max_length']}) can not be less than min_length ({kwargs.get('min_length', cls.min_length)})"
            )
        for field_name in ("max_count", "max_size", "sum_max_size"):
            if field_name in kwargs.keys() and kwargs[field_name] < 1:
                raise ValueError(
                    f"{field_name} ({kwargs[field_name]}) can not be less than 1"
                )
        if (
            kwargs.get('max_size')
            and kwargs.get('sum_max_size')
            and kwargs['max_size'] > kwargs['sum_max_size']
        ):
            raise ValueError(
                f"Max_size ({kwargs['max_size']}) must be less or equal sum_max_size ({kwargs['sum_max_size']})"
            )


class FieldImage(FieldFile):
    type_of = "image"
    min_width: int = 1
    min_height: int = 1
    max_width: int = 10000
    max_height: int = 10000
    __available_extensions = ('bmp', 'gif', 'jpg', 'jpeg', 'png', 'svg', 'tiff', 'webp')

    @classmethod
    def validate(cls, **kwargs):
        if 'extensions' in kwargs.keys():
            kwargs["extensions"] = tuple(
                set([el.lower() for el in kwargs.get("extensions", [])])
            )
        super().validate(**kwargs)
        for field_name in ("min_width", "min_height", "max_width", "max_height"):
            if kwargs.get(field_name, 1) < 1:
                raise ValueError(
                    f'{field_name} ({kwargs[field_name]}) can not be less than 1'
                )
        min_width = kwargs.get("min_width", cls.min_width)
        min_height = kwargs.get("min_height", cls.min_height)
        max_width = kwargs.get("max_width", cls.max_width)
        max_height = kwargs.get("max_height", cls.max_height)
        if min_height > max_height:
            raise ValueError(
                f"Min_height ({min_height}) can not be larger than max_height ({max_height})"
            )
        if min_width > max_width:
            raise ValueError(
                f"Min_width ({min_width}) can not be larger than max_width ({max_width})"
            )
        if diff := set(kwargs.get("extensions", ())).difference(
            cls.__available_extensions
        ):
            raise ValueError(f"There are not image extensions: {', '.join(diff)}")


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

    def get_all_fields(self) -> Iterator[str]:
        return self.Meta.all_fields

    def get_one_of_fields(self):
        """
        Groups of fields which cannot be filled together
        """
        all_fields_names = self.get_all_fields()
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
        all_fields_names = self.get_all_fields()
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

    def set_empty_value(self, params: dict, field: str) -> None:
        params[field] = ''
