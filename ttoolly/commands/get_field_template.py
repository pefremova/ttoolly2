import argparse
from pprint import pprint

from ttoolly.elements import elements_map


def add_arguments(parser):
    parser.add_argument(
        "types",
        help="Types of fields (example: field1:str field_int:int field_choice:choice)",
        nargs="+",
    )


def validate(el):
    try:
        name, field_type = el.split(":")
    except ValueError:
        raise AssertionError(
            f'Wrong format "{el}". Should be <field name>:<field type>'
        )
    choices = elements_map.keys()
    if field_type not in choices:
        raise AssertionError(
            f'Unexpected field type: "{field_type}" (choose from {", ".join(choices)})'
        )
    return name, field_type


def _main(types):
    res = {}
    for t in types:
        name, field_type = validate(t)
        model = elements_map[field_type]
        res[name] = model.get_template()
    pprint(res)
    exit()


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    _main(args.types)
