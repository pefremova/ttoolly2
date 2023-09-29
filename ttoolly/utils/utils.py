import string
import random
from faker import Faker
import re
import sys
import traceback

fake = Faker()


class continue_on_fail:
    def __init__(self, errors, *title, exc_types=(AssertionError,)):
        self.title = " ".join([str(t) for t in title])
        self.errors = errors
        self.exc_types = exc_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type and issubclass(exc_type, self.exc_types):
            self.errors.append(self.title + "\n" + get_error())
            return True


def convert_size_to_bytes(size: int | str) -> int:
    SYMBOLS = ["", "K", "M", "G"]
    size, symbol = re.findall(r"([\d\.]+)(\w?)", str(size))[0]
    size = float(size) * 1024 ** SYMBOLS.index(symbol if symbol in SYMBOLS else "")
    return int(size)


def get_error(tr_limit=None):
    etype, value, tb = sys.exc_info()
    err = ""
    if any([etype, value, tb]):
        err = "".join(
            [
                str(el)
                for el in traceback.format_exception(etype, value, tb, limit=tr_limit)
            ]
        )

    return err


def get_randname(l: int = 10, _type: str = "a", length_of_chunk: int = 10) -> str:
    """
    a - all
    d - digits
    w - letters
    p - punctuation
    s - whitespace
    """
    if "a" == _type:
        text = string.printable
    else:
        text = ""
        letters_dict = {
            "d": string.digits,
            "w": string.ascii_letters,
            "p": string.punctuation,
            "s": string.whitespace,
        }
        for t in _type:
            text += letters_dict.get(t, t)

    count_of_chunks = l // length_of_chunk
    n = "".join(
        [random.choice(text) for _ in range(length_of_chunk)]
    ) * count_of_chunks + "".join(
        [random.choice(text) for _ in range(l % length_of_chunk)]
    )
    return n


def get_all_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from get_all_subclasses(subclass)
        yield subclass


def get_random_domain_value(length):
    end_length = random.randint(2, min(length - 2, 6))
    domain_length = random.randint(1, min(length - end_length - 1, 62))
    subdomain_length = length - end_length - 1 - domain_length - 1
    if subdomain_length <= 1:
        subdomain = ""
        if subdomain_length >= 0:
            domain_length += 1 + subdomain_length
    else:
        subdomain = (
            f"{get_randname(1, 'w')}{get_randname(subdomain_length - 1, 'wd.-')}."
        )
        while any([len(el) > 62 for el in subdomain.split(".")]):
            subdomain = ".".join(
                [
                    (el if len(el) <= 62 else el[:61] + "." + el[62:])
                    for el in subdomain.split(".")
                ]
            )
        subdomain = re.sub(r"\.[\.\-]", ".%s" % get_randname(1, "w"), subdomain)
        subdomain = re.sub(r"\-\.", "%s." % get_randname(1, "w"), subdomain)
    if domain_length < 3:
        domain = get_randname(domain_length, "wd")
    else:
        domain = "%s%s%s" % (
            get_randname(1, "w"),
            get_randname(domain_length - 2, "wd-"),
            get_randname(1, "w"),
        )
        domain = re.sub(r"\-\-", "%s-" % get_randname(1, "w"), domain)

    return "%s%s.%s" % (subdomain, domain, get_randname(end_length, "w"))


def get_random_email_value(length, safe=False):
    """
    https://www.ietf.org/rfc/rfc2821.txt
    https://www.ietf.org/rfc/rfc3696.txt
    """
    MAX_USERNAME_LENGTH = 64
    min_length_without_name = 1 + 1 + 3  # @X.aa
    name_length = random.randint(
        min(2, length - min_length_without_name),
        min(MAX_USERNAME_LENGTH, length - min_length_without_name),
    )

    domain_length = length - name_length - 1  # <name>@<domain>
    symbols_for_generate = "wd"
    symbols_with_escaping = ""
    if not safe and name_length > 1:
        symbols_for_generate += "!#$%&'*+-/=?^_`{|}~."
        symbols_with_escaping = '\\"(),:;<>@[]'
        symbols_for_generate += symbols_with_escaping
    username = get_randname(name_length, symbols_for_generate)
    while ".." in username:
        username = username.replace("..", get_randname(1, "wd") + ".")
    for s in symbols_with_escaping:
        if s in username:
            username = username.replace(s, f"\{s}")[:name_length]
    username = re.sub(r"(\.$)|(^\.)|(\\$)", get_randname(1, "wd"), username)
    while len(username) < name_length:
        username += get_randname(1, "wd")
    domain = get_random_domain_value(domain_length)
    return f"{username}@{domain}".lower()
