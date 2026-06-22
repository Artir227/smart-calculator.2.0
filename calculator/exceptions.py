"""Exception hierarchy for the calculator package."""


class CalculatorError(Exception):
    """Base class for calculator-specific errors."""


class TokenizeError(CalculatorError):
    """Raised when an expression cannot be tokenized."""


class ParseError(CalculatorError):
    """Raised when an expression has invalid syntax."""


class EvaluationError(CalculatorError):
    """Raised when a syntactically valid expression cannot be evaluated."""
