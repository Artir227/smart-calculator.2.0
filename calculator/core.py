"""Public calculator orchestration API."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Literal

from .evaluator import Evaluator
from .exceptions import EvaluationError, ParseError
from .parser import Parser
from .tokenizer import tokenize

Number = float | int
AngleMode = Literal["rad", "deg"]


class Calculator:
    """Reusable calculator configured once and used for many expressions."""

    def __init__(
        self,
        *,
        verbose: bool = False,
        variables: Mapping[str, Number] | None = None,
        precision: int | None = None,
        angle_mode: AngleMode = "rad",
    ) -> None:
        if angle_mode not in {"rad", "deg"}:
            raise ValueError("angle_mode must be 'rad' or 'deg'")
        if precision is not None and precision < 0:
            raise ValueError("precision must be non-negative")
        self.verbose = verbose
        self.variables = dict(variables or {})
        self.precision = precision
        self.angle_mode = angle_mode

    def evaluate(self, expression: str) -> Number:
        """Evaluate a mathematical expression string."""

        if not expression or not expression.strip():
            raise ValueError("empty expression")
        tokens = tokenize(expression.strip())
        try:
            statements = Parser(tokens).parse_program()
        except ParseError:
            raise
        evaluator = Evaluator(
            variables=self.variables,
            angle_mode=self.angle_mode,
            verbose=self.verbose,
        )
        result = evaluator.evaluate_program(statements)
        return self._postprocess(result)

    def _postprocess(self, result: Number) -> Number:
        if self.precision is not None:
            result = round(result, self.precision)
        if isinstance(result, float):
            if math.isnan(result):
                raise EvaluationError("result is NaN")
            if result == 0:
                return 0
            if math.isfinite(result) and result.is_integer():
                return int(result)
        return result


def calculator(
    expression: str,
    *,
    verbose: bool = False,
    variables: dict[str, float | int] | None = None,
    precision: int | None = None,
    angle_mode: AngleMode = "rad",
) -> Number:
    """
    Evaluate a mathematical expression.

    Args:
        expression: expression string, for example ``"2+3*4"`` or ``"sqrt(16)"``.
        verbose: when true, log evaluation steps using ``logging``.
        variables: variable values available to the expression.
        precision: number of digits after the decimal point for rounding.
        angle_mode: trigonometry mode: ``"rad"`` or ``"deg"``.

    Returns:
        ``int`` when the result is mathematically integral, otherwise ``float``.
    """

    return Calculator(
        verbose=verbose,
        variables=variables,
        precision=precision,
        angle_mode=angle_mode,
    ).evaluate(expression)
