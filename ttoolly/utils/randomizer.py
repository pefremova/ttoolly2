import string
import random
import re
from datetime import datetime, time, timedelta
from dateutil import relativedelta


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


def get_random_datetime_value(
    datetime_from=None,
    datetime_to=None,
):
    month_start = datetime.combine(datetime.today().replace(day=1), time.min)
    month_end = (
        month_start + relativedelta.relativedelta(months=1) - timedelta(microseconds=1)
    )
    datetime_from = datetime_from or month_start
    datetime_to = datetime_to or month_end
    return datetime.fromtimestamp(
        random.randint(
            int(datetime_from.timestamp() * 10**6),
            int(datetime_to.timestamp() * 10**6),
        )
        / 10**6
    )


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
    if length < 3:  # a@b
        raise ValueError("Email length cannot be less than 3")
    if length < 6:  # a@b.cd
        username = get_randname(1, "wd")
        domain = get_randname(length - 2, "wd")
        return f"{username}@{domain}".lower()

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
            username = username.replace(s, fr"\{s}")[:name_length]
    username = re.sub(r"(\.$)|(^\.)|(\\$)", get_randname(1, "wd"), username)
    while len(username) < name_length:
        username += get_randname(1, "wd")
    domain = get_random_domain_value(domain_length)
    return f"{username}@{domain}".lower()
