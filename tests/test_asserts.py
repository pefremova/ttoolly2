import pytest

from ttoolly.asserts import common


@pytest.mark.parametrize(
    "dict1, dict2, expected_message",
    (
        ("q", {}, "First argument is not a dictionary"),
        (1, {}, "First argument is not a dictionary"),
        ((), {}, "First argument is not a dictionary"),
        ([], {}, "First argument is not a dictionary"),
        ({}, "q", "Second argument is not a dictionary"),
        ({}, 1, "Second argument is not a dictionary"),
        ({}, (), "Second argument is not a dictionary"),
        ({}, [], "Second argument is not a dictionary"),
        ({"qwe": 123}, {"qwe": {"a": 1}}, "[qwe]: 123 != %s" % repr({"a": 1})),
        (
            {
                "qwe": {
                    "a": 1,
                }
            },
            {"qwe": 123},
            "[qwe]: %s != 123" % repr({"a": 1}),
        ),
        (
            {
                "qwe": {
                    "a": 1,
                }
            },
            {"qwe": {"a": 1, "b": 1}},
            "[qwe]:\n  Not in first dict: [%s]" % repr("b"),
        ),
        (
            {"qwe": {"a": 1, "b": 1}},
            {"qwe": {"a": 1}},
            "[qwe]:\n  Not in second dict: [%s]" % repr("b"),
        ),
        (
            {"qwe": "q", "z": ""},
            {
                "qwe": 1,
            },
            "Not in second dict: [%s]\n[qwe]: %s != 1" % (repr("z"), repr("q")),
        ),
        ({"qwe": "й"}, {"qwe": "йцу"}, "[qwe]: й != йцу"),
        (
            {"qwe": "й".encode()},
            {"qwe": "йцу".encode()},
            f"[qwe]: {'й'.encode()} != {'йцу'.encode()}",
        ),
        (
            {"qwe": "й"},
            {"qwe": "йцу".encode()},
            "[qwe]: %s != %s" % (repr("й"), repr("йцу".encode())),
        ),
        (
            {"qwe": "й".encode()},
            {"qwe": "йцу"},
            "[qwe]: %s != %s" % (repr("й".encode()), repr("йцу")),
        ),
        (
            {"qwe": {"a": 1, "b": 2}},
            {"qwe": {"a": 2, "b": 1}},
            "[qwe]:\n  [qwe][a]: 1 != 2\n  [qwe][b]: 2 != 1",
        ),
        ({"qwe": [1]}, {"qwe": [1, 2]}, "[qwe]:\n[line 1]: Not in first list"),
        ({"qwe": ""}, {}, "Not in second dict: [%s]" % repr("qwe")),
        ({}, {"qwe": ""}, "Not in first dict: [%s]" % repr("qwe")),
    ),
)
def test_assert_dict_equal(dict1, dict2, expected_message):
    with pytest.raises(AssertionError) as exc_info:
        common.assert_dict_equal(dict1, dict2)
    assert str(exc_info.value) == expected_message


@pytest.mark.parametrize("custom_message", [None, "test"])
def test_assert_dict_equal_equal(custom_message):
    common.assert_dict_equal({"a": 1}, {"a": 1}, msg=custom_message)


@pytest.mark.parametrize(
    "list1, list2, expected_message",
    (
        ("q", [], "First argument is not a list"),
        ([], "q", "Second argument is not a list"),
        (
            [1],
            [1, 2],
            "[line 1]: Not in first list",
        ),
        ([{}], [{}, {"q": 1}], "[line 1]: Not in first list"),
        (
            [{"q": 1}, {"z": 2}],
            [{"w": 1}, {"z": 2}],
            "[line 0]: Not in first dict: [%s]\nNot in second dict: [%s]"
            % (repr("w"), repr("q")),
        ),
        (
            [[], [1]],
            [[], [1, 2]],
            "[line 1]: [line 1]: Not in first list",
        ),
        (
            [1, 2],
            [1],
            "[line 1]: Not in second list",
        ),
        ([{}, {"q": 1}], [{}], "[line 1]: Not in second list"),
        (
            [
                1,
            ],
            ["q"],
            "[line 0]: 1 != 'q'",
        ),
    ),
)
def test_assert_list_equal(list1, list2, expected_message):
    with pytest.raises(AssertionError) as exc_info:
        common.assert_list_equal(list1, list2)
    assert str(exc_info.value) == expected_message


@pytest.mark.parametrize("custom_message", [None, "test"])
def test_assert_list_equal_equal(custom_message):
    common.assert_list_equal([1, 2], [1, 2], custom_message)


@pytest.mark.parametrize(
    "new_count, initial_obj_count, additional, msg, expected_message",
    [
        (1, 1, 1, "", "Objects count is 1. Expected 2 (nothing created or deleted)"),
        (3, 1, 1, "", "Objects count is 3. Expected 2 (created 2)"),
        (2, 1, 0, "", "Objects count is 2. Expected 1 (created 1)"),
        (1, 2, 0, "", "Objects count is 1. Expected 2 (deleted 1)"),
        (1, 3, -1, "", "Objects count is 1. Expected 2 (deleted 2)"),
        (
            1,
            1,
            1,
            "After add",
            "After add objects count is 1. Expected 2 (nothing created or deleted)",
        ),
        (3, 1, 1, "After add", "After add objects count is 3. Expected 2 (created 2)"),
        (2, 1, 0, "After add", "After add objects count is 2. Expected 1 (created 1)"),
    ],
)
def test_assert_objects_count(
    new_count, initial_obj_count, additional, msg, expected_message
):
    with pytest.raises(AssertionError) as exc_info:
        common.assert_objects_count(new_count, initial_obj_count, additional, msg)
    assert str(exc_info.value) == expected_message


@pytest.mark.parametrize(
    "new_count, initial_obj_count, additional, msg",
    [
        (1, 1, 0, ""),
        (2, 1, 1, "test"),
        (3, 1, 2, ""),
        (1, 2, -1, "test"),
        (1, 3, -2, ""),
    ],
)
def test_assert_objects_count_equal(new_count, initial_obj_count, additional, msg):
    common.assert_objects_count(new_count, initial_obj_count, additional, msg)


@pytest.mark.parametrize(
    "form_errors, expected_message",
    [
        ("Error message", "There are errors on the form: Error message"),
        ({"qwe": 1}, 'There are errors on the form: {\n    "qwe": 1\n}'),
    ],
)
def test_assert_no_form_errors(form_errors, expected_message):
    with pytest.raises(AssertionError) as exc_info:
        common.assert_no_form_errors(form_errors)
    assert str(exc_info.value) == expected_message


@pytest.mark.parametrize("form_errors", [None, {}, ""])
def test_assert_no_form_errors_without_errors(form_errors):
    common.assert_no_form_errors(form_errors)


def test_assert_status_code():
    with pytest.raises(AssertionError) as exc_info:
        common.assert_status_code(100, 200)
    assert str(exc_info.value) == "Status code 100. Expected 200"


def test_assert_status_code_equal():
    common.assert_status_code(200, 200)
