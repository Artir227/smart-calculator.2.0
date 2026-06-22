"""Lexer for mathematical expressions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .exceptions import TokenizeError


class TokenType(str, Enum):
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    ASSIGN = "ASSIGN"
    EOF = "EOF"


@dataclass(frozen=True, slots=True)
class Token:
    type: TokenType
    value: str
    position: int


class Lexer:
    """Converts an input string into positioned tokens."""

    def __init__(self, expression: str) -> None:
        self.expression = expression
        self.length = len(expression)
        self.position = 0

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.position < self.length:
            char = self.expression[self.position]
            if char.isspace():
                self.position += 1
                continue
            if char.isdigit() or char == ".":
                tokens.append(self._read_number())
                continue
            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue
            if char == "(":
                tokens.append(Token(TokenType.LPAREN, char, self.position))
                self.position += 1
                continue
            if char == ")":
                tokens.append(Token(TokenType.RPAREN, char, self.position))
                self.position += 1
                continue
            if char == ",":
                tokens.append(Token(TokenType.COMMA, char, self.position))
                self.position += 1
                continue
            if char == ";":
                tokens.append(Token(TokenType.SEMICOLON, char, self.position))
                self.position += 1
                continue
            if char == "=":
                tokens.append(Token(TokenType.ASSIGN, char, self.position))
                self.position += 1
                continue
            if char in "+-*/%":
                tokens.append(self._read_operator())
                continue
            raise TokenizeError(
                f"unexpected character {char!r} at position {self.position}"
            )
        tokens.append(Token(TokenType.EOF, "", self.position))
        return tokens

    def _read_identifier(self) -> Token:
        start = self.position
        self.position += 1
        while self.position < self.length:
            char = self.expression[self.position]
            if not (char.isalnum() or char == "_"):
                break
            self.position += 1
        identifier = self.expression[start : self.position]
        return Token(TokenType.IDENTIFIER, identifier, start)

    def _read_operator(self) -> Token:
        start = self.position
        if self.expression.startswith("**", self.position):
            self.position += 2
            return Token(TokenType.OPERATOR, "**", start)
        if self.expression.startswith("//", self.position):
            self.position += 2
            return Token(TokenType.OPERATOR, "//", start)
        self.position += 1
        return Token(TokenType.OPERATOR, self.expression[start : self.position], start)

    def _read_number(self) -> Token:
        start = self.position
        saw_digit = False

        while self.position < self.length:
            char = self.expression[self.position]
            if char.isdigit():
                saw_digit = True
                self.position += 1
            elif char == "_":
                self.position += 1
            else:
                break

        if self.position < self.length and self.expression[self.position] == ".":
            self.position += 1
            while self.position < self.length:
                char = self.expression[self.position]
                if char.isdigit():
                    saw_digit = True
                    self.position += 1
                elif char == "_":
                    self.position += 1
                else:
                    break

        if not saw_digit:
            raise TokenizeError(f"unexpected character '.' at position {start}")

        if self.position < self.length and self.expression[self.position] in "eE":
            exp_position = self.position
            self.position += 1
            if self.position < self.length and self.expression[self.position] in "+-":
                self.position += 1
            exp_start = self.position
            while self.position < self.length:
                char = self.expression[self.position]
                if char.isdigit() or char == "_":
                    self.position += 1
                else:
                    break
            if exp_start == self.position:
                raise TokenizeError(f"invalid exponent at position {exp_position}")

        literal = self.expression[start : self.position]
        try:
            float(literal)
        except ValueError as exc:
            message = f"invalid number {literal!r} at position {start}"
            raise TokenizeError(message) from exc
        return Token(TokenType.NUMBER, literal, start)


def tokenize(expression: str) -> list[Token]:
    """Tokenize expression using the default lexer."""

    return Lexer(expression).tokenize()
