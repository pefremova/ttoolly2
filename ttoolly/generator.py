from functools import wraps
from inspect import signature, Parameter


def new_sig(func, attrs):
    sig = signature(func)
    # search if a VAR_POSITIONAL or VAR_KEYWORD is present
    # if yes insert parameter before it, else insert it in last position
    params = list(sig.parameters.values())
    for i, param in enumerate(params):
        if param.kind == Parameter.VAR_POSITIONAL:
            break
        if param.kind == Parameter.VAR_KEYWORD:
            break
    else:
        i = len(params)
    for name in attrs:
        newparam = Parameter(
            name, Parameter.POSITIONAL_OR_KEYWORD, default=Parameter.empty
        )
        params.insert(i, newparam)
    return sig.replace(parameters=params)


class TestCaseMeta(type):
    @classmethod
    def handle_case(mcs, cls, action):
        for cases_collection in cls.cases:
            for cases_class in cases_collection:
                for test in cases_class.get_tests(cls.form):
                    action(test)

    @classmethod
    def param_as_standalone_func(cls, func, name, **kwargs):
        """from parameterize.parameterized"""

        @wraps(func)
        def standalone_func(self, *a, **k):
            return func(self, *a, **k, **kwargs)

        standalone_func.__name__ = name

        # place_as is used by py.test to determine what source file should be
        # used for this test.
        standalone_func.place_as = func

        # Remove __wrapped__ because py.test will try to look at __wrapped__
        # to determine which parameters should be used with this test case,
        # and obviously we don't need it to do any parameterization.
        try:
            del standalone_func.__wrapped__
        except AttributeError:
            pass
        return standalone_func

    def __new__(mcs, name, bases, dct):
        cls = super(TestCaseMeta, mcs).__new__(mcs, name, bases, dct)

        def add_test(test):
            f = mcs.param_as_standalone_func(
                test._test,
                test.name,
                **test._kwargs,
            )
            sig = new_sig(
                f,
                getattr(cls, "additional_test_fixtures", []),
            )
            f.__signature__ = sig

            setattr(
                cls,
                test.name,
                f,
            )

        mcs.handle_case(cls, add_test)

        return cls
