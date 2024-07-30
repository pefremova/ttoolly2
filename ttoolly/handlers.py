from ttoolly.elements.common import Form
from typing import Iterator


class TestHandler:
    def __init__(self, form: Form):
        self.form = form

    def get_all_fields_cases(self) -> Iterator[tuple]:
        """
        Each element of the list contains all possible fields that can be filled together
        """
        all_fields_names = self.form.Meta.all_fields
        one_of_fields = self.form.get_one_of_fields()

        def check_fields_set_is_valid(fields_set):
            for name in fields_set:
                if one_of_fields[name] and all(
                    [
                        fields_set.intersection(other_fields)
                        for other_fields in one_of_fields[name]
                    ]
                ):
                    return False
            return True

        def filter_by_one_of(fields_set, n=0):
            res = set()
            if check_fields_set_is_valid(fields_set):
                res.add(tuple(sorted(fields_set)))
                return res
            for name in fields_set:
                for other_fields in one_of_fields[name]:
                    step_result = fields_set.copy()
                    if step_result.intersection(other_fields) == set(other_fields):
                        step_result.difference_update(other_fields)
                        if step_result != fields_set:
                            res.update(
                                [
                                    tuple(sorted(el))
                                    for el in filter_by_one_of(step_result, n=n + 1)
                                ]
                            )
                        else:
                            res.add(tuple(step_result))

                    step_result = fields_set.copy()
                    if step_result.intersection(other_fields) == set(other_fields):
                        step_result.discard(name)
                        if step_result != fields_set:
                            res.update(
                                [
                                    tuple(sorted(el))
                                    for el in filter_by_one_of(step_result, n=n + 1)
                                ]
                            )
                        else:
                            res.add(tuple(step_result))
            if not res:
                res.add(tuple(sorted(fields_set)))

            for el in res.copy():
                for el2 in res.copy():
                    if el != el2 and set(el2).intersection(el) == set(el):
                        res.discard(el)
            return res

        return filter_by_one_of(all_fields_names)

    def get_required_fields_cases(self) -> Iterator[tuple]:
        """
        Each element of the list contains all possible required fields that can be filled together
        """
        all_fields_names = self.form.Meta.all_fields

        main_required_fields = []
        required_with_case = []
        other_required_fields = []

        for name in all_fields_names:
            if required := self.form[name].required:
                if required.cases:
                    required_with_case.append(name)
                elif required.filled:
                    other_required_fields.append(name)
                else:
                    main_required_fields.append(name)
        all_required_fields = (
            main_required_fields + other_required_fields + required_with_case
        )
        result = {}
        for name in other_required_fields:
            required = self.form[name].required
            result[
                tuple(
                    sorted(set(all_required_fields).difference([name, required.filled]))
                )
            ] = {}

        for name in required_with_case:
            for required_case in self.form[name].required.cases:
                new_fields_list = set(all_required_fields).difference(
                    [k for k, v in required_case.items() if not v]
                )
                if set(all_required_fields).difference(new_fields_list):
                    result[tuple(sorted(new_fields_list))] = {}

                if additional_data := {k: v for k, v in required_case.items() if v}:
                    result[
                        tuple(
                            sorted(
                                main_required_fields
                                + [
                                    name,
                                ]
                            )
                        )
                    ] = additional_data

                    non_required_in_additional = tuple(
                        set(additional_data.keys()).difference(main_required_fields)
                    )
                    result[
                        tuple(
                            sorted(
                                set(main_required_fields).difference(
                                    (name,) + non_required_in_additional
                                )
                            )
                        )
                    ] = {
                        k: v
                        for k, v in additional_data.items()
                        if k not in non_required_in_additional
                    }

        if not result:
            result[tuple(main_required_fields)] = {}

        return result

    def get_not_empty_fields_cases(self) -> Iterator[tuple]:
        """
        Each element of the list contains all possible not empty fields that can be filled together
        """
        all_fields_names = self.form.Meta.all_fields

        main_not_empty_fields = []
        not_empty_with_case = []
        other_not_empty_fields = []

        for name in all_fields_names:
            if not_empty := self.form[name].not_empty:
                if not_empty.cases:
                    not_empty_with_case.append(name)
                elif not_empty.filled:
                    other_not_empty_fields.append(name)
                else:
                    main_not_empty_fields.append(name)
        all_not_empty_fields = (
            main_not_empty_fields + other_not_empty_fields + not_empty_with_case
        )
        result = {}
        for name in other_not_empty_fields:
            not_empty = self.form[name].not_empty
            result[
                tuple(
                    sorted(
                        set(all_not_empty_fields).difference([name, not_empty.filled])
                    )
                )
            ] = {}

        for name in not_empty_with_case:
            for not_empty_case in self.form[name].not_empty.cases:
                new_fields_list = set(all_not_empty_fields).difference(
                    [k for k, v in not_empty_case.items() if not v]
                )
                if set(all_not_empty_fields).difference(new_fields_list):
                    result[tuple(sorted(new_fields_list))] = {}

                if additional_data := {k: v for k, v in not_empty_case.items() if v}:
                    result[
                        tuple(
                            sorted(
                                main_not_empty_fields
                                + [
                                    name,
                                ]
                            )
                        )
                    ] = additional_data

                    non_not_empty_in_additional = tuple(
                        set(additional_data.keys()).difference(main_not_empty_fields)
                    )
                    result[
                        tuple(
                            sorted(
                                set(main_not_empty_fields).difference(
                                    (name,) + non_not_empty_in_additional
                                )
                            )
                        )
                    ] = {
                        k: v
                        for k, v in additional_data.items()
                        if k not in non_not_empty_in_additional
                    }

        if not result:
            result[tuple(main_not_empty_fields)] = {}

        return result
