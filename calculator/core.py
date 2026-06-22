"""Public orchestration layer for the calculator package."""

from __future__ import annotations

import math
from typing import Literal, Mapping, Optional, Union

from .evaluator import Evaluator
from .parser import Parser
from .tokenizer import Lexer

Number = Union[int, float]


class Calculator:
    """Production-ready mathematical expression calculator."""

    def __init__(
        self,
        *,
        verbose: bool = False,
        variables: Optional[Mapping[str, Number]] = None,
        precision: Optional[int] = None,
        angle_mode: Literal["rad", "deg"] = "rad",
    ) -> None:
        if precision is not None and precision < 0:
            raise ValueError("precision must be non-negative or None")
        if angle_mode not in {"rad", "deg"}:
            raise ValueError("angle_mode must be 'rad' or 'deg'")
        self.verbose = verbose
        self.variables = dict(variables or {})
        self.precision = precision
        self.angle_mode = angle_mode

    def evaluate(self, expression: str) -> Number:
        """Evaluate a mathematical expression and return int for integer results."""
        if not isinstance(expression, str):
            raise TypeError("expression must be a string")
        if not expression.strip():
            raise ValueError("empty expression")

        tokens = Lexer(expression.strip()).tokenize()
        program = Parser(tokens).parse()
        result = Evaluator(
            variables=self.variables,
            angle_mode=self.angle_mode,
            verbose=self.verbose,
        ).evaluate(program)
        return self._postprocess(result)

    def _postprocess(self, result: float) -> Number:
        if self.precision is not None:
            result = round(result, self.precision)
        if result == 0:
            return 0
        if math.isfinite(result) and result.is_integer():
            return int(result)
        return result


def calculator(
    expression: str,
    *,
    verbose: bool = False,
    variables: Optional[Mapping[str, Number]] = None,
    precision: Optional[int] = None,
    angle_mode: Literal["rad", "deg"] = "rad",
) -> Number:
    """
    Evaluate a mathematical expression.

    Args:
        expression: expression string, e.g. "2+3*4", "sqrt(16)", "x*y+1".
        verbose: if True, log evaluation steps using logging.
        variables: variable values passed into expression evaluation.
        precision: number of digits after the decimal point for final rounding.
        angle_mode: trigonometric angle mode: "rad" or "deg".

    Returns:
        int if the final result is mathematically integral, otherwise float.
    """
    return Calculator(
        verbose=verbose,
        variables=variables,
        precision=precision,
        angle_mode=angle_mode,
    ).evaluate(expression)
