from ttoolly import utils
import re
import pytest


@pytest.mark.parametrize(
    "text,expected",
    [
        (10, 10),
        (36192, 36192),
        ("2K", 1024 * 2),
        ("12M", 1024 * 1024 * 12),
        ("1G", 1024**3),
    ],
)
def test_convert_size_to_bytes(text, expected):
    assert utils.convert_size_to_bytes(text) == expected


def test_get_randname_short_d():
    value = utils.get_randname(5, "d")
    assert len(value) == 5
    assert value.isdigit()


def test_get_randname_long_d():
    value = utils.get_randname(25, "d")
    assert len(value) == 25
    assert value.isdigit()
    assert value[:10] == value[10:20]


def test_get_randname_long_with_chunk_length_d():
    value = utils.get_randname(15, "d", 5)
    assert len(value) == 15
    assert value.isdigit()
    assert value[:5] == value[5:10] == value[10:]


def test_get_randname_short_w():
    value = utils.get_randname(5, "w")
    assert len(value) == 5
    assert re.match(r"[a-zA-Z]{5}", value)


def test_get_randname_long_w():
    value = utils.get_randname(25, "w")
    assert len(value) == 25
    assert re.match(r"([a-zA-Z]{10})\1[a-zA-Z]{5}", value)


def test_get_randname_long_with_chunk_length_w():
    value = utils.get_randname(15, "w", 5)
    assert len(value) == 15
    assert re.match(r"([a-zA-Z]{5})\1\1", value)


def test_get_randname_short_p():
    value = utils.get_randname(5, "p")
    assert len(value) == 5
    assert re.match(r'[\[!"#$%&\'\(\)*+,-./:;<=>?@[\\\]^_`{|}~\]]{5}', value)


def test_get_randname_short_s():
    value = utils.get_randname(5, "s")
    assert len(value) == 5
    assert re.match(r"\s{5}", value)


def test_get_randname_short_custom():
    value = utils.get_randname(5, "-")
    assert value == "-" * 5


def test_get_randname_long_all():
    value = utils.get_randname(25, "a")
    assert len(value) == 25
    assert re.match(r"([\s\S]{10})\1[\s\S]{5}", value, re.MULTILINE)


def test_get_randname_long_with_chunk_length_all():
    value = utils.get_randname(15, "a", 5)
    assert len(value) == 15
    assert re.match(r"([\s\S]{5})\1\1", value, re.MULTILINE)


def test_get_randname_long_all_default():
    value = utils.get_randname(25)
    assert len(value) == 25
    assert re.match(r"([\s\S]{10})\1[\s\S]{5}", value, re.MULTILINE)


def test_get_all_subclasses():
    class A:
        pass

    class B(A):
        pass

    class C(B):
        pass

    assert set(utils.get_all_subclasses(A)).symmetric_difference([B, C]) == set()


@pytest.mark.parametrize("length", [10, 62, 63, 500])
def test_get_random_domain_value(length):
    value = utils.get_random_domain_value(length)
    assert len(value) == length
    assert re.match(
        r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]",
        value,
        re.IGNORECASE,
    )


@pytest.mark.parametrize("length", [10, 254, 255, 256, 500])
def test_get_random_email_value(length):
    value = utils.get_random_email_value(length)
    """https://www.rfc-editor.org/rfc/rfc3696"""
    "https://www.ietf.org/rfc/rfc3696.txt"
    assert len(value) == length
    assert re.match(
        r"(^([a-zA-Z0-9!#$%&\'*+\-/=?^_`{|}~]|(\\ )|(\\)|(\\\")|(\\\()|(\\\))|(\\,)|(\\:)|(\\;)|(\\<)|(\\>)|(\\@)|(\\\[)|(\\\]))(([a-zA-Z0-9!#$%&\'*+\-/=?^_`{|}~.]|(\\ )|(\\)|(\\\")|(\\\()|(\\\))|(\\,)|(\\:)|(\\;)|(\\<)|(\\>)|(\\@)|(\\\[)|(\\\])){0,63})"
        '|(^"[a-zA-Z0-9!#$%&\'*+\-/=?^_`{|}~.\\(),:;<>@\[\] ]{1,62}"))'
        r"@(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]",
        value,
    )
    assert ".." not in value
    assert ".@" not in value
