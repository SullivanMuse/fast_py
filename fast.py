#!/usr/bin/env python3

# Builtin imports
import argparse
import sys

# Project imports
import colors
from parse import statements


def parse(args):
    for file in args.input:
        if r := statements(file.read()):
            r.val.pprint()
        else:
            print(f"{colors.error}{r}{colors.reset}")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parse_parser = subparsers.add_parser("parse", help="parse command")
    parse_parser.add_argument(
        "input",
        nargs="*",
        type=argparse.FileType(),
        default=[sys.stdin],
        help="Files to parse",
    )
    parse_parser.set_defaults(func=parse)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
