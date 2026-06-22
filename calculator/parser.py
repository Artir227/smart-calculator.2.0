"""Recursive-descent parser for calculator expressions."""

from __future__ import annotations

from typing import List

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
from .exceptions import ParseError
from .tokenizer import Token, TokenType


class Parser:
    """Parses tokens into an abstract syntax tree."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ProgramNode:
        statements: List[ASTNode] = []
        if self._peek().type == TokenType.EOF:
            raise ValueError("empty expression")

        while self._peek().type != TokenType.EOF:
            if self._peek().type == TokenType.SEMICOLON:
                raise ParseError("empty statement")
            statements.append(self._statement())
            if self._match(TokenType.SEMICOLON):
                if self._peek().type == TokenType.EOF:
                    break
                continue
            if self._peek().type != TokenType.EOF:
                token = self._peek()
                raise ParseError(
                    f"unexpected token {token.value!r} at position {token.position}"
                )

        return ProgramNode(statements)

    def _statement(self) -> ASTNode:
        if (
            self._peek().type == TokenType.IDENTIFIER
            and self._peek_next().type == TokenType.ASSIGN
        ):
            name = self._advance().value
            self._advance()
            if name in {"pi", "e", "tau", "inf"}:
                raise ParseError(f"cannot assign to constant {name!r}")
            return AssignmentNode(name, self._expression())
        return self._expression()

    def _expression(self) -> ASTNode:
        node = self._term()
        while self._match_operator("+", "-"):
            operator = self._previous().value
            right = self._term()
            node = BinaryOpNode(operator, node, right)
        return node

    def _term(self) -> ASTNode:
        node = self._unary()
        while self._match_operator("*", "/", "//", "%"):
            operator = self._previous().value
            right = self._unary()
            node = BinaryOpNode(operator, node, right)
        return node

    def _unary(self) -> ASTNode:
        if self._match_operator("+", "-"):
            operator = self._previous().value
            return UnaryOpNode(operator, self._unary())
        return self._power()

    def _power(self) -> ASTNode:
        node = self._postfix()
        if self._match_operator("**"):
            right = self._unary()
            node = BinaryOpNode("**", node, right)
        return node

    def _postfix(self) -> ASTNode:
        node = self._primary()
        while self._is_unary_percent():
            self._advance()
            node = PercentNode(node)
        return node

    def _primary(self) -> ASTNode:
        if self._match(TokenType.NUMBER):
            raw = self._previous().value.replace("_", "")
            try:
                return NumberNode(float(raw))
            except ValueError as exc:
                raise ParseError(f"invalid number {self._previous().value!r}") from exc

        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            if self._match(TokenType.LPAREN):
                args = self._argument_list(name)
                self._consume(TokenType.RPAREN, "unbalanced parentheses")
                return FunctionCallNode(name, args)
            return VariableNode(name)

        if self._match(TokenType.LPAREN):
            node = self._expression()
            self._consume(TokenType.RPAREN, "unbalanced parentheses")
            return node

        token = self._peek()
        if token.type == TokenType.RPAREN:
            raise ParseError("unbalanced parentheses")
        raise ParseError(f"expected expression at position {token.position}")

    def _argument_list(self, function_name: str) -> List[ASTNode]:
        if self._peek().type == TokenType.RPAREN:
            if function_name in {"min", "max"}:
                raise ParseError(f"{function_name}() takes at least 1 argument, got 0")
            return []

        args = [self._expression()]
        while self._match(TokenType.COMMA):
            if self._peek().type == TokenType.RPAREN:
                raise ParseError("expected expression after comma")
            args.append(self._expression())
        return args

    def _is_unary_percent(self) -> bool:
        if not (self._peek().type == TokenType.OPERATOR and self._peek().value == "%"):
            return False
        next_token = self._peek_next()
        # If the next token can start an operand, percent is binary modulo.
        return next_token.type not in {
            TokenType.NUMBER,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
        }

    def _match_operator(self, *operators: str) -> bool:
        if self._peek().type == TokenType.OPERATOR and self._peek().value in operators:
            self._advance()
            return True
        return False

    def _match(self, token_type: TokenType) -> bool:
        if self._peek().type == token_type:
            self._advance()
            return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._peek().type == token_type:
            return self._advance()
        raise ParseError(message)

    def _advance(self) -> Token:
        if self._peek().type != TokenType.EOF:
            self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _peek_next(self) -> Token:
        if self.current + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + 1]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
