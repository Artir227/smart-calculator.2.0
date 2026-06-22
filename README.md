# Production Calculator

[![CI](https://github.com/OWNER/REPOSITORY/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPOSITORY/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/OWNER/REPOSITORY/branch/main/graph/badge.svg)](https://codecov.io/gh/OWNER/REPOSITORY)
[![PyPI](https://img.shields.io/pypi/v/production-calculator.svg)](https://pypi.org/project/production-calculator/)

Production-ready Python library for evaluating mathematical expressions from strings.
The project contains a tokenizer, recursive-descent parser, AST evaluator, tests,
typing configuration, and GitHub Actions workflows.

## Features

- Binary operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Unary operators: `+x`, `-x`, postfix percent like `50%`
- Nested parentheses
- Integers, floats, scientific notation, and underscores: `1.5e3`, `1_000`
- Constants: `pi`, `e`, `tau`, `inf`
- Functions: `sqrt`, `abs`, `pow`, `min`, `max`, `floor`, `ceil`, `round`,
  `log`, `log10`, `ln`, `exp`, `sin`, `cos`, `tan`, `factorial`
- Variables via `variables={...}`
- Optional assignments: `x = 2; x * 3`
- Precision control and degree/radian modes for trigonometry
- Custom exception hierarchy

## Installation for development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Usage

```python
from calculator import calculator, Calculator

assert calculator("2 + 3 * 4") == 14
assert calculator("sqrt(16)") == 4
assert calculator("x * y + 1", variables={"x": 5, "y": 10}) == 51
assert calculator("sin(90)", angle_mode="deg") == 1
assert calculator("10 / 3", precision=2) == 3.33
assert calculator("a = 1; b = a + 2; a + b") == 4

calc = Calculator(variables={"x": 3}, precision=3)
assert calc.evaluate("sqrt(x)") == 1.732
```

## Public API

```python
def calculator(
    expression: str,
    *,
    verbose: bool = False,
    variables: Mapping[str, int | float] | None = None,
    precision: int | None = None,
    angle_mode: Literal["rad", "deg"] = "rad",
) -> int | float:
    ...
```

A `Calculator` class with the same constructor parameters and an
`evaluate(expression: str)` method is also available.

## Error handling

The package exposes the following calculator-specific exceptions:

- `CalculatorError`
- `TokenizeError`
- `ParseError`
- `EvaluationError`

Division by zero intentionally raises Python's built-in `ZeroDivisionError`.
An empty expression raises `ValueError`.

## Development checks

```bash
black --check calculator/ tests/
flake8 calculator/ tests/
mypy --strict calculator/
ruff check calculator/ tests/
pytest tests/ -v --cov=calculator --cov-report=xml --cov-fail-under=90
```

## Architecture

The evaluation pipeline is:

```text
Input string -> Lexer -> Parser -> AST -> Evaluator -> Post-processing -> Result
```

Tokenization, parsing, and evaluation are split into separate modules to make the
code easy to test and extend.

## Notes

- Built-in constants have priority over values passed in `variables`.
- Assignments mutate a local copy of variables, not the caller's dictionary.
- `round(x)` uses half-up rounding for intuitive calculator behavior.
- `-2**2` is parsed as `-(2**2)`, so the result is `-4`.
