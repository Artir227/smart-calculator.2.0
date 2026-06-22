"""Recursive-descent parser for calculator expressions."""

from __future__ import annotations

from .ast_nodes import (
    AssignmentNode,
    BinaryOpNode,
    FunctionCallNode,
    Node,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)
from .exceptions import ParseError
from .tokenizer import Token, TokenType


class Parser:
    """Builds AST statements from tokens."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.position = 0

    def parse_program(self) -> list[Node]:
        statements: list[Node] = []
        if self._current().type == TokenType.EOF:
            raise ParseError("empty expression")
        while self._current().type != TokenType.EOF:
            if self._current().type == TokenType.SEMICOLON:
                position = self._current().position
                raise ParseError(f"empty statement at position {position}")
            statements.append(self._parse_statement())
            if self._match(TokenType.SEMICOLON):
                if self._current().type == TokenType.EOF:
                    break
                continue
            if self._current().type != TokenType.EOF:
                raise ParseError(
                    f"unexpected token {self._current().value!r} "
                    f"at position {self._current().position}"
                )
        return statements

    def _parse_statement(self) -> Node:
        if (
            self._current().type == TokenType.IDENTIFIER
            and self._peek().type == TokenType.ASSIGN
        ):
            name = self._advance().value
            self._advance()
            return AssignmentNode(name, self._parse_expression())
        return self._parse_expression()

    def _parse_expression(self) -> Node:
        return self._parse_additive()

    def _parse_additive(self) -> Node:
        node = self._parse_multiplicative()
        while self._current().type == TokenType.OPERATOR and self._current().value in {
            "+",
            "-",
        }:
            operator = self._advance().value
            node = BinaryOpNode(operator, node, self._parse_multiplicative())
        return node

    def _parse_multiplicative(self) -> Node:
        node = self._parse_unary()
        while self._current().type == TokenType.OPERATOR and self._current().value in {
            "*",
            "/",
            "//",
            "%",
        }:
            operator = self._advance().value
            node = BinaryOpNode(operator, node, self._parse_unary())
        return node

    def _parse_unary(self) -> Node:
        if self._current().type == TokenType.OPERATOR and self._current().value in {
            "+",
            "-",
        }:
            operator = self._advance().value
            return UnaryOpNode(operator, self._parse_unary())
        return self._parse_power()

    def _parse_power(self) -> Node:
        node = self._parse_postfix()
        if self._current().type == TokenType.OPERATOR and self._current().value == "**":
            operator = self._advance().value
            node = BinaryOpNode(operator, node, self._parse_unary())
        return node

    def _parse_postfix(self) -> Node:
        node = self._parse_primary()
        while (
            self._current().type == TokenType.OPERATOR
            and self._current().value == "%"
            and not self._is_operand_start(self._peek())
        ):
            self._advance()
            node = UnaryOpNode("%", node)
        return node

    def _parse_primary(self) -> Node:
        token = self._current()
        if token.type == TokenType.NUMBER:
            self._advance()
            return NumberNode(self._number_value(token.value))
        if token.type == TokenType.IDENTIFIER:
            return self._parse_identifier_or_function()
        if token.type == TokenType.LPAREN:
            self._advance()
            node = self._parse_expression()
            if not self._match(TokenType.RPAREN):
                raise ParseError("unbalanced parentheses")
            return node
        message = f"unexpected token {token.value!r} at position {token.position}"
        raise ParseError(message)

    def _parse_identifier_or_function(self) -> Node:
        name_token = self._advance()
        if self._match(TokenType.LPAREN):
            args: list[Node] = []
            if self._current().type != TokenType.RPAREN:
                while True:
                    args.append(self._parse_expression())
                    if not self._match(TokenType.COMMA):
                        break
            if not self._match(TokenType.RPAREN):
                raise ParseError("unbalanced parentheses")
            return FunctionCallNode(name_token.value, args)
        return VariableNode(name_token.value)

    def _current(self) -> Token:
        return self.tokens[self.position]

    def _peek(self) -> Token:
        if self.position + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position + 1]

    def _advance(self) -> Token:
        token = self._current()
        self.position += 1
        return token

    def _match(self, token_type: TokenType) -> bool:
        if self._current().type == token_type:
            self._advance()
            return True
        return False

    @staticmethod
    def _number_value(value: str) -> float | int:
        numeric = float(value)
        if numeric.is_integer() and "." not in value and "e" not in value.lower():
            return int(value.replace("_", ""))
        return numeric

    @staticmethod
    def _is_operand_start(token: Token) -> bool:
        return token.type in {TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LPAREN}
