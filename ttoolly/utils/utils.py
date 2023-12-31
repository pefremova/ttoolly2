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


def get_all_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from get_all_subclasses(subclass)
        yield subclass
