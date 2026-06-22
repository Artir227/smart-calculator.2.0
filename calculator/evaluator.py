"""AST evaluator for the calculator package."""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping
from typing import Dict, Optional, Union

from .ast_nodes import (
    AssignmentNode,
    ASTNode,
    BinaryOpNode,
    FunctionCallNode,
    NumberNode,
    PercentNode,
    ProgramNode,
    UnaryOpNode,
    VariableNode,
)
from .constants import CONSTANTS
from .exceptions import EvaluationError
from .functions import FUNCTIONS

Number = Union[int, float]
LOGGER = logging.getLogger(__name__)


class Evaluator:
    """Evaluates AST nodes in a local variable context."""

    def __init__(
        self,
        *,
        variables: Optional[Mapping[str, Number]] = None,
        angle_mode: str = "rad",
        verbose: bool = False,
    ) -> None:
        if angle_mode not in {"rad", "deg"}:
            raise ValueError("angle_mode must be 'rad' or 'deg'")
        self.context: Dict[str, float] = {
            key: float(value) for key, value in (variables or {}).items()
        }
        self.angle_mode = angle_mode
        self.verbose = verbose

    def evaluate(self, node: ASTNode) -> float:
        result = self._eval(node)
        self._validate_number(result)
        return result

    def _eval(self, node: ASTNode) -> float:
        if isinstance(node, ProgramNode):
            return self._program(node)
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, VariableNode):
            return self._variable(node)
        if isinstance(node, UnaryOpNode):
            return self._unary(node)
        if isinstance(node, PercentNode):
            return self._percent(node)
        if isinstance(node, BinaryOpNode):
            return self._binary(node)
        if isinstance(node, FunctionCallNode):
            return self._function(node)
        if isinstance(node, AssignmentNode):
            return self._assignment(node)
        raise EvaluationError(f"unsupported AST node {type(node).__name__}")

    def _program(self, node: ProgramNode) -> float:
        if not node.statements:
            raise EvaluationError("empty program")
        result = 0.0
        for statement in node.statements:
            result = self._eval(statement)
        return result

    def _variable(self, node: VariableNode) -> float:
        if node.name in CONSTANTS:
            return CONSTANTS[node.name]
        if node.name not in self.context:
            raise EvaluationError(f"unknown variable {node.name!r}")
        return self.context[node.name]

    def _assignment(self, node: AssignmentNode) -> float:
        value = self._eval(node.expression)
        self.context[node.name] = value
        self._log("assign %s = %s", node.name, value)
        return value

    def _unary(self, node: UnaryOpNode) -> float:
        operand = self._eval(node.operand)
        if node.operator == "+":
            result = +operand
        elif node.operator == "-":
            result = -operand
        else:
            raise EvaluationError(f"unsupported unary operator {node.operator!r}")
        self._log("%s%s -> %s", node.operator, operand, result)
        return result

    def _percent(self, node: PercentNode) -> float:
        operand = self._eval(node.operand)
        result = operand / 100.0
        self._log("%s%% -> %s", operand, result)
        return result

    def _binary(self, node: BinaryOpNode) -> float:
        left = self._eval(node.left)
        right = self._eval(node.right)
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
            try:
                result = left**right
            except (OverflowError, ValueError) as exc:
                raise EvaluationError(str(exc)) from exc
        else:
            raise EvaluationError(f"unsupported binary operator {operator!r}")
        self._validate_number(result)
        self._log("%s %s %s -> %s", left, operator, right, result)
        return float(result)

    def _function(self, node: FunctionCallNode) -> float:
        if node.name not in FUNCTIONS:
            raise EvaluationError(f"unknown function {node.name!r}")
        args = [self._eval(argument) for argument in node.args]
        try:
            result = FUNCTIONS[node.name](args, self.angle_mode)
        except ValueError as exc:
            raise EvaluationError(str(exc)) from exc
        self._validate_number(result)
        self._log("%s(%s) -> %s", node.name, ", ".join(map(str, args)), result)
        return float(result)

    def _validate_number(self, value: float) -> None:
        if math.isnan(value):
            raise EvaluationError("result is not a number")

    def _log(self, message: str, *args: object) -> None:
        if self.verbose:
            LOGGER.info(message, *args)
