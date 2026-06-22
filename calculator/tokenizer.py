"""Lexer for mathematical expressions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

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


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int


_NUMBER_RE = re.compile(
    r"""
    (?:(?:\d(?:_?\d)*)?\.\d(?:_?\d)*|\d(?:_?\d)*(?:\.\d(?:_?\d)*)?)
    (?:[eE][+-]?\d(?:_?\d)*)?
    """,
    re.VERBOSE,
)
_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_OPERATORS = ("**", "//", "+", "-", "*", "/", "%")


class Lexer:
    """Turns an input expression into a list of tokens with positions."""

    def __init__(self, expression: str) -> None:
        self.expression = expression

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        index = 0
        length = len(self.expression)

        while index < length:
            char = self.expression[index]
            if char.isspace():
                index += 1
                continue

            number = self._match(_NUMBER_RE, index)
            if number is not None:
                tokens.append(Token(TokenType.NUMBER, number, index))
                index += len(number)
                continue

            identifier = self._match(_IDENTIFIER_RE, index)
            if identifier is not None:
                tokens.append(Token(TokenType.IDENTIFIER, identifier, index))
                index += len(identifier)
                continue

            if char == "(":
                tokens.append(Token(TokenType.LPAREN, char, index))
                index += 1
                continue
            if char == ")":
                tokens.append(Token(TokenType.RPAREN, char, index))
                index += 1
                continue
            if char == ",":
                tokens.append(Token(TokenType.COMMA, char, index))
                index += 1
                continue
            if char == ";":
                tokens.append(Token(TokenType.SEMICOLON, char, index))
                index += 1
                continue
            if char == "=":
                tokens.append(Token(TokenType.ASSIGN, char, index))
                index += 1
                continue

            matched_operator = None
            for operator in _OPERATORS:
                if self.expression.startswith(operator, index):
                    matched_operator = operator
                    break
            if matched_operator is not None:
                tokens.append(Token(TokenType.OPERATOR, matched_operator, index))
                index += len(matched_operator)
                continue

            raise TokenizeError(f"unexpected character {char!r} at position {index}")

        tokens.append(Token(TokenType.EOF, "", length))
        return tokens

    def _match(self, pattern: re.Pattern[str], index: int) -> Optional[str]:
        match = pattern.match(self.expression, index)
        return match.group(0) if match else None
