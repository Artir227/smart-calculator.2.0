"""AST nodes used by the recursive-descent parser."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Node:
    """Base AST node."""


@dataclass(frozen=True, slots=True)
class NumberNode(Node):
    value: float | int


@dataclass(frozen=True, slots=True)
class VariableNode(Node):
    name: str


@dataclass(frozen=True, slots=True)
class UnaryOpNode(Node):
    operator: str
    operand: Node


@dataclass(frozen=True, slots=True)
class BinaryOpNode(Node):
    operator: str
    left: Node
    right: Node


@dataclass(frozen=True, slots=True)
class FunctionCallNode(Node):
    name: str
    args: list[Node]


@dataclass(frozen=True, slots=True)
class AssignmentNode(Node):
    name: str
    value: Node
