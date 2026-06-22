"""AST evaluator for calculator expressions."""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping

from .ast_nodes import (
    AssignmentNode,
    BinaryOpNode,
    FunctionCallNode,
    Node,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)
from .constants import CONSTANTS
from .exceptions import EvaluationError
from .functions import FUNCTIONS, Number

LOGGER = logging.getLogger(__name__)


class Evaluator:
    """Evaluates AST statements using a local variable context."""

    def __init__(
        self,
        *,
        variables: Mapping[str, float | int] | None = None,
        angle_mode: str = "rad",
        verbose: bool = False,
    ) -> None:
        self.variables: dict[str, Number] = dict(variables or {})
        self.angle_mode = angle_mode
        self.verbose = verbose

    def evaluate_program(self, statements: list[Node]) -> Number:
        result: Number = 0
        for statement in statements:
            result = self.evaluate(statement)
        return result

    def evaluate(self, node: Node) -> Number:
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, VariableNode):
            return self._evaluate_variable(node)
        if isinstance(node, UnaryOpNode):
            return self._evaluate_unary(node)
        if isinstance(node, BinaryOpNode):
            return self._evaluate_binary(node)
        if isinstance(node, FunctionCallNode):
            return self._evaluate_function(node)
        if isinstance(node, AssignmentNode):
            value = self.evaluate(node.value)
            self.variables[node.name] = value
            self._log("assign %s = %s", node.name, value)
            return value
        raise EvaluationError(f"unsupported node {type(node).__name__}")

    def _evaluate_variable(self, node: VariableNode) -> Number:
        if node.name in CONSTANTS:
            return CONSTANTS[node.name]
        if node.name in self.variables:
            return self.variables[node.name]
        raise EvaluationError(f"unknown variable {node.name!r}")

    def _evaluate_unary(self, node: UnaryOpNode) -> Number:
        operand = self.evaluate(node.operand)
        if node.operator == "+":
            result = +operand
        elif node.operator == "-":
            result = -operand
        elif node.operator == "%":
            result = operand / 100
        else:
            raise EvaluationError(f"unknown unary operator {node.operator!r}")
        self._log("%s%s -> %s", node.operator, operand, result)
        return result

    def _evaluate_binary(self, node: BinaryOpNode) -> Number:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        operator = node.operator
        if operator == "+":
            result = left + right
        elif operator == "-":
            result = left - right
        elif operator == "*":
            result = left * right
        elif operator == "/":
            if right == 0:
                raise ZeroDivisionError("division by zero")
            result = left / right
        elif operator == "//":
            if right == 0:
                raise ZeroDivisionError("division by zero")
            result = left // right
        elif operator == "%":
            if right == 0:
                raise ZeroDivisionError("division by zero")
            result = left % right
        elif operator == "**":
            result = left**right
        else:
            raise EvaluationError(f"unknown operator {operator!r}")
        self._ensure_not_nan(result)
        self._log("%s %s %s -> %s", left, operator, right, result)
        return result

    def _evaluate_function(self, node: FunctionCallNode) -> Number:
        if node.name not in FUNCTIONS:
            raise EvaluationError(f"unknown function {node.name!r}")
        args = [self.evaluate(arg) for arg in node.args]
        result = FUNCTIONS[node.name](args, self.angle_mode)
        self._ensure_not_nan(result)
        self._log("%s(%s) -> %s", node.name, ", ".join(map(str, args)), result)
        return result

    def _log(self, message: str, *args: object) -> None:
        if self.verbose:
            LOGGER.info(message, *args)

    @staticmethod
    def _ensure_not_nan(value: Number) -> None:
        if isinstance(value, float) and math.isnan(value):
            raise EvaluationError("result is NaN")
