from copy import deepcopy

import pytest
from ttoolly.elements.common import Form
from ttoolly.handlers import TestHandler


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"f1": {}}, set((("f1",),))),
        ({"f1": {"only": {"if": {"f2": None}}}, "f2": {}}, set((("f1",), ("f2",)))),
        ({"f1": {"only": {"if": {"f2": 123}}}, "f2": {}}, set((("f1", "f2"),))),
        (
            {
                "f1": {"only": {"if": {"f2": None}}},
                "f2": {"only": {"if": {"f1": None, "f3": None}}},
                "f3": {"only": {"if": {"f2": None}}},
            },
            set((("f1", "f3"), ("f2",))),
        ),
        (
            {
                "f1": {"only": {"if": {"f2": None}}},
                "f2": {"only": {"if": {"f1": None}}},
            },
            set((("f1",), ("f2",))),
        ),
        # TODO: conflicting ifs ({"f1": {"only": {"if": {"f2": 2}}}, "f2": {}, "f3": {"only": {"if": {"f2": 3}}}}, set((("f1", "f2"), ("f2", "f3"))))
    ],
)
def test_get_all_fields_cases(config, expected):
    _config = deepcopy(config)
    for el in _config.values():
        el.update({"type": "str", "max_length": 10})
    form = Form(**{"fields": _config})

    assert TestHandler(form).get_all_fields_cases() == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"f1": {"required": True}, "f2": {}}, {("f1",): {}}),
        ({"f1": {"required": {"if": "f2"}}, "f2": {}}, {(): {}}),
        (
            {
                "f1": {"required": {"if": {"f2": None}}},
                "f2": {"required": {"if": {"f1": None}}},
                "f3": {"required": True},
            },
            {("f1", "f3"): {}, ("f2", "f3"): {}},
        ),
        (
            {
                "f1": {"required": {"if": {"f2": None}}},
                "f2": {"required": {"if": {"f1": None, "f3": None}}},
                "f3": {"required": {"if": {"f2": None}}},
            },
            {("f1", "f3"): {}, ("f2",): {}},
        ),
        (
            {
                "f1": {"required": {"if": {"f3": 1}}},
                "f2": {"required": {"if": {"f4": 2}}},
                "f3": {},
                "f4": {},
            },
            {("f1",): {"f3": 1}, ("f2",): {"f4": 2}, (): {}},
        ),
    ],
)
def test_get_required_fields_cases(config, expected):
    _config = deepcopy(config)
    for el in _config.values():
        el.update({"type": "str", "max_length": 10})
    form = Form(**{"fields": _config})

    assert TestHandler(form).get_required_fields_cases() == expected
