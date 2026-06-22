"""Registry of safe mathematical functions supported by the calculator."""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable, Dict, List, Tuple

from .exceptions import EvaluationError, ParseError

MathFunction = Callable[[List[float], str], float]


def _require_arity(name: str, args: List[float], expected: int) -> None:
    if len(args) != expected:
        raise ParseError(f"{name}() takes {expected} argument, got {len(args)}")


def _to_angle(value: float, angle_mode: str) -> float:
    return math.radians(value) if angle_mode == "deg" else value


def _round_half_up(value: float) -> float:
    return float(Decimal(str(value)).to_integral_value(rounding=ROUND_HALF_UP))


def _one_arg(name: str, fn: Callable[[float], float]) -> MathFunction:
    def wrapped(args: List[float], angle_mode: str) -> float:
        del angle_mode
        _require_arity(name, args, 1)
        return float(fn(args[0]))

    return wrapped


def _sqrt(args: List[float], angle_mode: str) -> float:
    del angle_mode
    _require_arity("sqrt", args, 1)
    if args[0] < 0:
        raise EvaluationError("cannot take sqrt of negative number")
    return math.sqrt(args[0])


def _log(name: str, fn: Callable[[float], float]) -> MathFunction:
    def wrapped(args: List[float], angle_mode: str) -> float:
        del angle_mode
        _require_arity(name, args, 1)
        if args[0] <= 0:
            raise EvaluationError(f"{name}() domain error")
        return float(fn(args[0]))

    return wrapped


def _pow(args: List[float], angle_mode: str) -> float:
    del angle_mode
    _require_arity("pow", args, 2)
    return float(math.pow(args[0], args[1]))


def _min(args: List[float], angle_mode: str) -> float:
    del angle_mode
    if not args:
        raise ParseError("min() takes at least 1 argument, got 0")
    return min(args)


def _max(args: List[float], angle_mode: str) -> float:
    del angle_mode
    if not args:
        raise ParseError("max() takes at least 1 argument, got 0")
    return max(args)


def _round(args: List[float], angle_mode: str) -> float:
    del angle_mode
    _require_arity("round", args, 1)
    return _round_half_up(args[0])


def _sin(args: List[float], angle_mode: str) -> float:
    _require_arity("sin", args, 1)
    return math.sin(_to_angle(args[0], angle_mode))


def _cos(args: List[float], angle_mode: str) -> float:
    _require_arity("cos", args, 1)
    return math.cos(_to_angle(args[0], angle_mode))


def _tan(args: List[float], angle_mode: str) -> float:
    _require_arity("tan", args, 1)
    return math.tan(_to_angle(args[0], angle_mode))


def _factorial(args: List[float], angle_mode: str) -> float:
    del angle_mode
    _require_arity("factorial", args, 1)
    value = args[0]
    if not math.isfinite(value) or not value.is_integer() or value < 0:
        raise EvaluationError("factorial requires non-negative integer")
    integer_value = int(value)
    if integer_value > 10000:
        raise EvaluationError("factorial argument is too large")
    return float(math.factorial(integer_value))


FUNCTIONS: Dict[str, MathFunction] = {
    "sqrt": _sqrt,
    "abs": _one_arg("abs", abs),
    "pow": _pow,
    "min": _min,
    "max": _max,
    "floor": _one_arg("floor", math.floor),
    "ceil": _one_arg("ceil", math.ceil),
    "round": _round,
    "log": _log("log", math.log),
    "ln": _log("ln", math.log),
    "log10": _log("log10", math.log10),
    "exp": _one_arg("exp", math.exp),
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "factorial": _factorial,
}

ARITY: Dict[str, Tuple[int, int]] = {
    "sqrt": (1, 1),
    "abs": (1, 1),
    "pow": (2, 2),
    "min": (1, 10_000),
    "max": (1, 10_000),
    "floor": (1, 1),
    "ceil": (1, 1),
    "round": (1, 1),
    "log": (1, 1),
    "ln": (1, 1),
    "log10": (1, 1),
    "exp": (1, 1),
    "sin": (1, 1),
    "cos": (1, 1),
    "tan": (1, 1),
    "factorial": (1, 1),
}
