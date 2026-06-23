#!/usr/bin/env python3
"""CLI calculator with argparse."""

import argparse
import sys


class TooManyNumbersError(Exception):
    """Raised when more than two numbers are provided."""


def check_numbers(count: int) -> None:
    if count > 2:
        raise TooManyNumbersError("Too many numbers: exactly 2 are required.")
    if count < 2:
        parser.error("the following arguments are required: two numbers")


def format_number(n: float) -> str:
    if n == int(n):
        return f"{int(n)}.0"
    return str(n)


def main() -> None:
    global parser
    parser = argparse.ArgumentParser(description="CLI calculator")
    parser.add_argument("numbers", nargs="+", type=float, help="Exactly two numbers")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", action="store_true", help="Addition")
    group.add_argument("--sub", action="store_true", help="Subtraction")
    group.add_argument("--mul", action="store_true", help="Multiplication")
    group.add_argument("--div", action="store_true", help="Division")
    parser.add_argument("--float", dest="use_float", action="store_true", help="Float division (/)")
    parser.add_argument("--int", dest="use_int", action="store_true", help="Integer division (//)")

    args = parser.parse_args()

    try:
        check_numbers(len(args.numbers))
    except TooManyNumbersError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    a, b = args.numbers[0], args.numbers[1]
    fa, fb = format_number(a), format_number(b)

    if args.add:
        result = a + b
        op = "+"
    elif args.sub:
        result = a - b
        op = "-"
    elif args.mul:
        result = a * b
        op = "*"
    else:
        if b == 0:
            print("error: division by zero", file=sys.stderr)
            sys.exit(1)
        if args.use_float and args.use_int:
            print("warning: both --float and --int specified; using float division", file=sys.stderr)
            use_float_div = True
        elif args.use_int:
            use_float_div = False
        elif args.use_float:
            use_float_div = True
        else:
            print("info: no division mode specified; using float division", file=sys.stderr)
            use_float_div = True
        if use_float_div:
            result = a / b
            op = "/"
        else:
            result = a // b
            op = "//"

    print(f"{fa} {op} {fb} = {format_number(result)}")


if __name__ == "__main__":
    main()
