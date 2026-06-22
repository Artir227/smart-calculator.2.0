"""AST node definitions used by the parser and evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


class ASTNode:
    """Base class for AST nodes."""


@dataclass(frozen=True)
class NumberNode(ASTNode):
    value: float


@dataclass(frozen=True)
class VariableNode(ASTNode):
    name: str


@dataclass(frozen=True)
class UnaryOpNode(ASTNode):
    operator: str
    operand: ASTNode


@dataclass(frozen=True)
class BinaryOpNode(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode


@dataclass(frozen=True)
class PercentNode(ASTNode):
    operand: ASTNode


@dataclass(frozen=True)
class FunctionCallNode(ASTNode):
    name: str
    args: List[ASTNode]


@dataclass(frozen=True)
class AssignmentNode(ASTNode):
    name: str
    expression: ASTNode


@dataclass(frozen=True)
class ProgramNode(ASTNode):
    statements: List[ASTNode]
