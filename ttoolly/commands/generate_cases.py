import argparse
import os
from ttoolly.elements.common import Form
from ttoolly.generator import TestCaseMeta
from ttoolly.testcases import CasesAdd
import importlib


def add_arguments(parser):
    parser.add_argument(
        "config_path",
        help="Path to form config. Example: test/path/form.json",
    )
    parser.add_argument(
        "--fields",
        dest="fields",
        help="Path to custom form fields. Example: test.path.fields",
        nargs="*",
    )
    parser.add_argument(
        "--humanable",
        dest="humanable",
        help="Show human readable cases",
        action="store_true",
    )


def _main(data, humanable=False):
    mcs = TestCaseMeta

    class T:
        form = Form(**data)
        cases = [
            CasesAdd,
        ]

    def print_test(test):
        print()
        print()
        print(getattr(test, {False: "get_code", True: "get_steps"}[humanable])())

    mcs.handle_case(T, print_test)


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loader = None
    _, ext = os.path.splitext(args.config_path)
    for fields_path in args.fields or []:
        importlib.import_module(fields_path)

    if ext.lower() in (".json", ""):
        from ttoolly.loaders import JsonLoader

        loader = JsonLoader
    if not loader:
        raise Exception(f"Unknown config format {args.config_path}")
    data = loader(args.config_path).data

    _main(data, args.humanable)
