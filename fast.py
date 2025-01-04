#!/usr/bin/env python3

# Builtin imports
import argparse
import sys

# Project imports
import colors
from parse_statements import statements


def parse(args):
    if args.command is not None:
        if r := statements(args.command):
            r.val.pprint()
        else:
            print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")
    for file in args.input:
        if r := statements(file.read()):
            r.val.pprint()
        else:
            print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")


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
    parse_parser.add_argument("-c", "--command", default=None, help="Command to execute directly")
    parse_parser.set_defaults(func=parse)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
