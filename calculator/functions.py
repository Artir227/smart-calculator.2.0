"""Safe mathematical function registry."""

from __future__ import annotations

import math
from collections.abc import Callable
from decimal import Decimal, ROUND_HALF_UP

from .exceptions import EvaluationError, ParseError

Number = float | int
Function = Callable[[list[Number], str], Number]


def _require_arity(name: str, args: list[Number], arity: int) -> None:
    if len(args) != arity:
        raise ParseError(f"{name}() takes {arity} argument, got {len(args)}")


def _require_min_arity(name: str, args: list[Number], arity: int) -> None:
    if len(args) < arity:
        raise ParseError(f"{name}() takes at least {arity} argument, got {len(args)}")


def _round_half_up(value: Number) -> int:
    return int(Decimal(str(value)).to_integral_value(rounding=ROUND_HALF_UP))


def _sqrt(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("sqrt", args, 1)
    if args[0] < 0:
        raise EvaluationError("cannot take sqrt of negative number")
    return math.sqrt(args[0])


def _abs(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("abs", args, 1)
    return abs(args[0])


def _pow(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("pow", args, 2)
    return args[0] ** args[1]


def _min(args: list[Number], _angle_mode: str) -> Number:
    _require_min_arity("min", args, 1)
    return min(args)


def _max(args: list[Number], _angle_mode: str) -> Number:
    _require_min_arity("max", args, 1)
    return max(args)


def _floor(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("floor", args, 1)
    return math.floor(args[0])


def _ceil(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("ceil", args, 1)
    return math.ceil(args[0])


def _round(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("round", args, 1)
    return _round_half_up(args[0])


def _log(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("log", args, 1)
    if args[0] <= 0:
        raise EvaluationError("log is defined only for positive numbers")
    return math.log(args[0])


def _log10(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("log10", args, 1)
    if args[0] <= 0:
        raise EvaluationError("log10 is defined only for positive numbers")
    return math.log10(args[0])


def _exp(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("exp", args, 1)
    return math.exp(args[0])


def _to_radians(value: Number, angle_mode: str) -> float:
    if angle_mode == "deg":
        return math.radians(value)
    return float(value)


def _sin(args: list[Number], angle_mode: str) -> Number:
    _require_arity("sin", args, 1)
    return math.sin(_to_radians(args[0], angle_mode))


def _cos(args: list[Number], angle_mode: str) -> Number:
    _require_arity("cos", args, 1)
    return math.cos(_to_radians(args[0], angle_mode))


def _tan(args: list[Number], angle_mode: str) -> Number:
    _require_arity("tan", args, 1)
    return math.tan(_to_radians(args[0], angle_mode))


def _factorial(args: list[Number], _angle_mode: str) -> Number:
    _require_arity("factorial", args, 1)
    value = args[0]
    if isinstance(value, float) and not value.is_integer():
        raise EvaluationError("factorial requires non-negative integer")
    integer_value = int(value)
    if integer_value < 0:
        raise EvaluationError("factorial requires non-negative integer")
    return math.factorial(integer_value)


FUNCTIONS: dict[str, Function] = {
    "sqrt": _sqrt,
    "abs": _abs,
    "pow": _pow,
    "min": _min,
    "max": _max,
    "floor": _floor,
    "ceil": _ceil,
    "round": _round,
    "log": _log,
    "ln": _log,
    "log10": _log10,
    "exp": _exp,
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "factorial": _factorial,
}
