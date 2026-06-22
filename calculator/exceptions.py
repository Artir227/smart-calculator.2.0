"""Calculator exception hierarchy."""


class CalculatorError(Exception):
    """Base class for all calculator-specific errors."""


class TokenizeError(CalculatorError):
    """Raised when an expression cannot be tokenized."""


class ParseError(CalculatorError):
    """Raised when tokens do not form a valid expression."""


class EvaluationError(CalculatorError):
    """Raised when a valid expression cannot be evaluated."""
