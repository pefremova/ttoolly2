def check_instance_fields(obj, params):
    result = {}
    for field_name, expected_value in params.items():
        value = getattr(obj, field_name)
        if hasattr(value, "__dict__") and isinstance(expected_value, dict):
            if _result := check_instance_fields(value, expected_value):
                result[field_name] = _result
        elif value != expected_value:
            result[field_name] = f"{value!r} != {expected_value!r}"
    if result:
        return result


def assert_instance_fields(obj, params):
    if res := check_instance_fields(obj, params):
        raise AssertionError(f"{res!r}")
