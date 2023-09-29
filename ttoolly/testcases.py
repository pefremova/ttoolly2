from ttoolly.elements.common import Form
import inspect
from typing import Iterator
from ttoolly.handlers import TestHandler
from inspect import signature
import re
from pprint import pformat


def impact(*a, **k):
    pass


def type_of(*a, **k):
    pass


class CaseContainer:
    def check(self, form: Form) -> bool:
        return True


class Case:
    def __init__(self, f, name, description="", **kwargs):
        self._test = f
        self._kwargs = kwargs
        self.name = name
        self.description = description

    def get_code(self):
        code = inspect.getsource(self._test)
        sig = signature(self._test)
        indent = re.findall("^( *)def ", code)[0]
        code = re.sub(f"(^|\n){indent}", r"\1", code)

        first_line, other_code = code.split("\n", 1)
        first_line = re.sub("def (.+?)\(self,", f"def {self.name}(self,", first_line)
        first_line = first_line.replace("*args,", "")
        params = list(sig.parameters.values())
        other_kwargs = {}
        for p in params:
            if p.name in self._kwargs.keys():
                value = self._kwargs.pop(p.name)
                if p.name == "form":
                    form = value
                else:
                    other_kwargs[p.name] = value
                if not callable(value):
                    first_line = re.sub(
                        f"({p.name},?|{p.name}=.+?,?)",
                        "",
                        first_line,
                    )
                    if form == value:
                        continue
                    other_code = f"{indent}{indent}{p.name}={value}\n" + other_code
        other_code = f"{indent}kwargs = {self._kwargs}\n" + other_code
        first_line = re.sub(",\s*\*\*kwargs", "", first_line)
        code = first_line + "\n" + other_code
        for call_form_method in re.findall("form\..+?\(.+?\)", code):
            method_name = re.findall("form.(.+?)\(", call_form_method)[0]
            method = getattr(form, method_name)
            arguments = {}
            for _argument in re.findall("form\..+?\((.+?)\)", call_form_method)[
                0
            ].split(","):
                argument_name, *argument_value = _argument.split("=", 1)
                argument_name = argument_name.strip()
                if argument_value:
                    argument_value = argument_value[0].strip()
                if argument_value and argument_value in other_kwargs.keys():
                    arguments[argument_name] = other_kwargs[argument_value]
                if argument_value == []:
                    arguments[argument_name] = other_kwargs[argument_name]

            new_code = pformat(method(**arguments))
            code = code.replace(call_form_method, new_code)
        return code

    def get_steps(self):
        def format_value(v):
            if not v:
                return v
            if isinstance(v, (list, tuple)):
                return "* " + "\n* ".join(v)
            if isinstance(v, dict):
                return "* " + "\n* ".join([f"{kk}={vv}" for kk, vv in v])
            return v

        if callable(self.description):
            return self.description(
                **{k: format_value(v) for k, v in self._kwargs.items()}
            )
        return self.description.format(
            **{k: format_value(v) for k, v in self._kwargs.items()}
        )


class CaseAdd_all_filled(CaseContainer):
    description = (
        "NAME: All possible fields are filled"
        "\n\nDETAILS: Send create request with filled fields:\n{fields}"
        "\n\nRESULT: Object should be created successfully"
    )

    def _test(self, form, fields, *args, **kwargs):
        self.prepare_for_add(**kwargs)
        params = form.get_random_data(fields)
        snapshot = self.take_snapshot()
        response = self.send_add(params, **kwargs)
        self.check_success_add(response, snapshot)

    @classmethod
    def get_tests(self, form: Form) -> Iterator:
        return [
            Case(
                self._test,
                name=f'test_add_all_filled_{i}_{"_".join(fields)}',
                description=self.description,
                form=form,
                fields=fields,
            )
            for i, fields in enumerate(TestHandler(form).get_all_fields_cases())
        ]


class CaseAdd_without_not_required(CaseContainer):
    @staticmethod
    def description(**kwargs):
        description = (
            "NAME: Non required fields are not filled"
            "\n\nDETAILS: Send create request with\n# fields filled with any correct data:\n{fields}"
        )
        if kwargs["additional"]:
            description += "\nFields filled with particular data:\n{additional}"
        description += "\n\nRESULT: Object should be created successfully"
        return description.format(**kwargs)

    def _test(self, form, fields, additional, *args, **kwargs):
        self.prepare_for_add(**kwargs)
        params = form.get_random_data(fields, additional=additional)
        snapshot = self.take_snapshot()
        response = self.send_add(params, **kwargs)
        self.check_success_add(response, snapshot)

    @classmethod
    def get_tests(self, form: Form) -> Iterator:
        return [
            Case(
                self._test,
                name=f'test_add_without_not_required_{i}_{"_".join(fields)}',
                description=self.description,
                form=form,
                additional=additional_params,
                fields=fields,
            )
            for i, (fields, additional_params) in enumerate(
                TestHandler(form).get_required_fields_cases().items()
            )
        ]


CasesAdd = [
    CaseAdd_all_filled,
    CaseAdd_without_not_required,
]
