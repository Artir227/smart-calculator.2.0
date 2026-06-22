# Mathematical Expression Calculator

![CI](https://github.com/USERNAME/math-expression-calculator/actions/workflows/ci.yml/badge.svg)
![Codecov](https://codecov.io/gh/USERNAME/math-expression-calculator/branch/main/graph/badge.svg)
![PyPI](https://img.shields.io/pypi/v/math-expression-calculator.svg)

Production-ready Python library for evaluating mathematical expressions from strings. The project exposes a library API only: no CLI, REPL, web interface, symbolic algebra, plots, or complex numbers.

## Features

- Binary operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Unary operators: `+x`, `-x`, postfix percent such as `50%`
- Parentheses with arbitrary nesting depth within Python recursion limits
- Numbers: integers, floats, scientific notation, underscores, optional `.5` format
- Constants: `pi`, `e`, `tau`, `inf`
- Functions: `sqrt`, `abs`, `pow`, `min`, `max`, `floor`, `ceil`, `round`, `log`, `log10`, `ln`, `exp`, `sin`, `cos`, `tan`, `factorial`
- Variables through `variables={...}`
- Assignment chains such as `x = 2; x * 3`
- `precision`, `angle_mode`, and verbose logging support
- Custom exception hierarchy: `CalculatorError`, `TokenizeError`, `ParseError`, `EvaluationError`

## Installation for development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e .[dev]
```

## Usage

```python
from calculator import calculator, Calculator

assert calculator("2+3*4") == 14
assert calculator("sqrt(16)") == 4
assert calculator("x*y+1", variables={"x": 5, "y": 10}) == 51
assert calculator("sin(90)", angle_mode="deg") == 1
assert calculator("10/3", precision=2) == 3.33
assert calculator("x = 2; x * 3", variables={}) == 6

calc = Calculator(variables={"x": 10}, precision=2)
assert calc.evaluate("x / 3") == 3.33
```

## Public API

```python
def calculator(
    expression: str,
    *,
    verbose: bool = False,
    variables: dict[str, float | int] | None = None,
    precision: int | None = None,
    angle_mode: Literal["rad", "deg"] = "rad",
) -> int | float: ...
```

`Calculator` has the same configuration parameters in the constructor and exposes `evaluate(expression: str)`.

## Architecture

The expression pipeline is:

```text
input string
-> normalization
-> tokenization with positioned tokens
-> recursive-descent parser
-> AST
-> evaluator
-> post-processing: precision and int/float coercion
-> result
```

Recommended package layout from the assignment is implemented:

```text
calculator/
├── __init__.py
├── ast_nodes.py
├── constants.py
├── core.py
├── evaluator.py
├── exceptions.py
├── functions.py
├── parser.py
└── tokenizer.py
```

## Operator details

Exponentiation is right-associative:

```python
calculator("2**3**2")  # 512
```

Unary minus follows the requested behavior:

```python
calculator("-2**2")    # -4
calculator("(-2)**2")  # 4
```

Postfix percent is supported:

```python
calculator("50%")       # 0.5
calculator("200*10%")   # 20
calculator("(100+50)%") # 1.5
```

Binary remainder is also supported:

```python
calculator("17%5")  # 2
```

## Error handling

```python
from calculator import TokenizeError, ParseError, EvaluationError
```

- Empty expression: `ValueError`
- Unexpected character: `TokenizeError`
- Invalid syntax / parentheses / arity: `ParseError`
- Unknown variable/function and math domain errors: `EvaluationError`
- Division by zero: `ZeroDivisionError`

## Quality checks

```bash
black --check calculator/ tests/
flake8 calculator/ tests/
mypy --strict calculator/
ruff check calculator/ tests/
pytest tests/ -v --cov=calculator --cov-report=xml --cov-fail-under=90
bandit -r calculator/
python -m build
python -m twine check dist/*
```

## Complexity

Tokenization, parsing, and evaluation are linear in the input size: `O(n)` time and `O(n)` memory.
