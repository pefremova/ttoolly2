import json


def assert_no_form_errors(form_errors):
    if form_errors:
        if isinstance(form_errors, dict):
            form_errors = json.dumps(form_errors, indent=4, ensure_ascii=False)
        raise AssertionError(f"There are errors on the form: {form_errors}")


def assert_objects_count(new_count, initial_obj_count=0, additional=1, msg=""):
    if new_count != initial_obj_count + additional:
        diff = new_count - initial_obj_count
        if diff < 0:
            diff_msg = f"deleted {abs(diff)}"
        elif diff > 0:
            diff_msg = f"created {diff}"
        else:
            diff_msg = "nothing created or deleted"

        _msg = f'{(msg + " o") if msg else "O"}bjects count is {new_count}. Expected {initial_obj_count+additional} ({diff_msg})'
        raise AssertionError(_msg)


def assert_status_code(response_status_code, expected_status_code):
    if response_status_code != expected_status_code:
        raise AssertionError(
            f"Status code {response_status_code}. Expected {expected_status_code}"
        )


def _get_dict_diff(d1, d2, parent_key=""):
    text = []
    parent_key = "[%s]" % parent_key.strip("[]") if parent_key else ""
    not_in_second = set(d1.keys()).difference(d2.keys())
    not_in_first = set(d2.keys()).difference(d1.keys())
    if not_in_first:
        text.append(f"Not in first dict: {list(not_in_first)!r}")
    if not_in_second:
        text.append(f"Not in second dict: {list(not_in_second)!r}")
    for key in set(d1.keys()).intersection(d2.keys()):
        if d1[key] != d2[key]:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                res = _get_dict_diff(d1[key], d2[key], parent_key + f"[{key}]")
                if res:
                    text.append(
                        parent_key + f"[{key}]:\n  " + "\n  ".join(res.splitlines())
                    )
            elif isinstance(d1[key], list) and isinstance(d2[key], list):
                list_diff = _get_list_diff(d1[key], d2[key])
                if list_diff:
                    text.append(
                        f'{parent_key if parent_key else ""}[{key}]:\n{list_diff}'
                    )
            else:
                d1_value = d1[key]
                d2_value = d2[key]
                if type(d1_value) != type(d2_value):
                    d1_value = repr(d1_value)
                    d2_value = repr(d2_value)

                text.append(
                    f'{parent_key if parent_key else ""}[{key}]: {d1_value} != {d2_value}'
                )
    res = "\n".join(text)
    return res


def _get_list_diff(l1, l2):
    errors = []
    for i in range(max(len(l1), len(l2))):
        if i >= len(l1):
            errors.append(f"[line {i}]: Not in first list")
        if i >= len(l2):
            errors.append(f"[line {i}]: Not in second list")

        l1_value = l1[i]
        l2_value = l2[i]
        if l1_value == l2_value:
            continue

        if isinstance(l1_value, dict) and isinstance(l2_value, dict):
            dict_diff = _get_dict_diff(l1_value, l2_value)
            if dict_diff:
                errors.append(f"[line {i}]: {dict_diff}")
        elif isinstance(l1_value, list) and isinstance(l2_value, list):
            list_diff = _get_list_diff(l1_value, l2_value)
            if list_diff:
                errors.append(f"[line {i}]: {list_diff}")
        else:
            if type(l1_value) != type(l2_value):
                d1_value = repr(l1_value)
                d2_value = repr(l2_value)

            errors.append(f"[line {i}]: {d1_value} != {d2_value}")

    res = "\n".join(errors)
    return res


def assert_dict_equal(d1, d2, msg=None):
    msg = msg + ":\n" if msg else ""

    if d1 != d2:
        diff = _get_dict_diff(d1, d2)
        if diff:
            raise AssertionError(diff)
