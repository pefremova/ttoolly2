from ttoolly.testcases import Case
import pytest


def test_get_code():
    def _test(self, form, arg1, arg2, *args, **kwargs):
        self.fun1(**kwargs)
        a = form.func1(arg=arg2)
        b = form.func1(arg1)
        self.fun2(a)

    class MockForm:
        def func1(self, arg):
            return arg

    testcase = Case(
        _test,
        name=f"test_name",
        form=MockForm(),
        arg1="value1",
        arg2=(1, 2, 3),
        arg3=3,
    )
    text = (
        """def test_name(self):"""
        """\n    kwargs = {'arg3': 3}"""
        """\n    arg2 = (1, 2, 3)"""
        """\n    arg1 = \'value1\'"""
        """\n    self.fun1(**kwargs)"""
        """\n    a = (1, 2, 3)"""
        """\n    b = \'value1\'"""
        """\n    self.fun2(a)\n"""
    )
    assert testcase.get_code() == text


@pytest.mark.parametrize(
    "description,test_kwargs,expected",
    [
        ("test description", {}, "test description"),
        ("test description {a}", {"a": 123}, "test description 123"),
        ("test description {a}", {"a": []}, "test description []"),
        ("test description {a}", {"a": None}, "test description None"),
        ("test description {a}", {"a": ""}, "test description "),
        (
            "test description {a}",
            {"a": ("value1", "value2", "value3")},
            "test description * value1\n* value2\n* value3",
        ),
        (
            "test description {a}",
            {"a": ["value1", "value2", "value3"]},
            "test description * value1\n* value2\n* value3",
        ),
        (
            "test description {a}",
            {"a": {"k1": "v1", "k2": "v2"}},
            "test description * k1=v1\n* k2=v2",
        ),
    ],
)
def test_get_description(description, test_kwargs, expected):
    testcase = Case(
        lambda *a, **k: None, name=f"test_name", description=description, **test_kwargs
    )
    assert testcase.get_steps() == expected


def test_get_callable_description():
    def d(a, b=2):
        return f"text {a} " + str(b * 2)

    testcase = Case(lambda *a, **k: None, name=f"test_name", description=d, a=2, b=10)
    assert testcase.get_steps() == "text 2 20"
