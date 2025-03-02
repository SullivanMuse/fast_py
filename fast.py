#!/usr/bin/env python3

import argparse

import colors
from compile import Compiler
from parse import statements


def parse(args):
    if args.command is not None:
        if r := statements(args.command):
            for statement in r.val:
                print(statement)
        else:
            print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")
    for file in args.input:
        if r := statements(file.read()):
            for statement in r.val:
                print(statement)
        else:
            print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")


def compile(args):
    compiler = Compiler()
    if args.command is not None:
        if r := statements(args.command):
            expr = r.val
            print("(Statements)")
            for statement in expr:
                print(statement)
            compiler.compile(expr)
            print()
            print("(Code)")
            for code in compiler.code:
                print(code)
        else:
            print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")
    for file in args.input:
        if r := statements(file.read()):
            expr = r.val
            if r := compiler.compile(expr):
                print(r.val)
            else:
                print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")
        else:
            print(f"{colors.error}error {r.span.start}: {r.reason}{colors.reset}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        nargs="*",
        type=argparse.FileType(),
        default=[],
        help="Files to parse",
    )
    parser.add_argument(
        "-c", "--command", default=None, help="Command to execute directly"
    )

    subparsers = parser.add_subparsers(required=True)

    # Parse subcommand
    parse_parser = subparsers.add_parser("parse", help="parse input")
    parse_parser.set_defaults(func=parse)

    # Compile subcommand
    compile_parser = subparsers.add_parser("compile", help="compile to bytecode")
    compile_parser.set_defaults(func=compile)

    args = parser.parse_args()

    # print(f"{args = }")

    args.func(args)


if __name__ == "__main__":
    main()
