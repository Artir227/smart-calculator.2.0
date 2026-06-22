from __future__ import annotations

import math

import pytest

from calculator import EvaluationError, ParseError, TokenizeError, calculator


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2+3", 5),
        ("10-4", 6),
        ("6*7", 42),
        ("15/3", 5),
        ("15/4", 3.75),
        ("17%5", 2),
        ("17//5", 3),
        ("50%", 0.5),
        ("200*10%", 20),
        ("(100+50)%", 1.5),
        ("2+3*4", 14),
        ("(2+3)*4", 20),
        ("10-2*3", 4),
        ("100/10/2", 5),
        ("10-20+5", -5),
        ("2*3+4*5", 26),
        ("2**3", 8),
        ("2**3**2", 512),
        ("2**10", 1024),
        ("-2**2", -4),
        ("(-2)**2", 4),
        ("9**0.5", 3),
        ("0**0", 1),
        ("2**-1", 0.5),
        ("-5+3", -2),
        ("--5", 5),
        ("- -5", 5),
        ("+5", 5),
        ("3*-2", -6),
        ("3*(-2)", -6),
        ("-(2+3)", -5),
    ],
)
def test_operations(expression: str, expected: float | int) -> None:
    assert calculator(expression) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sqrt(16)", 4),
        ("sqrt(2)", math.sqrt(2)),
        ("abs(-5)", 5),
        ("abs(-3.7)", 3.7),
        ("pow(2, 10)", 1024),
        ("pow(2, 0.5)", math.sqrt(2)),
        ("min(3, 1, 2)", 1),
        ("max(3, 1, 2)", 3),
        ("min(5)", 5),
        ("floor(3.7)", 3),
        ("ceil(3.2)", 4),
        ("round(3.5)", 4),
        ("log(e)", 1),
        ("ln(e)", 1),
        ("log10(1000)", 3),
        ("exp(0)", 1),
        ("exp(1)", math.e),
        ("sin(0)", 0),
        ("cos(0)", 1),
        ("factorial(0)", 1),
        ("factorial(5)", 120),
        ("factorial(10)", 3628800),
    ],
)
def test_functions(expression: str, expected: float | int) -> None:
    assert calculator(expression) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize(
    ("expression", "angle_mode", "expected"),
    [
        ("sin(0)", "rad", 0),
        ("sin(pi/2)", "rad", 1),
        ("sin(90)", "deg", 1),
        ("cos(0)", "rad", 1),
        ("cos(60)", "deg", 0.5),
        ("tan(45)", "deg", 1),
    ],
)
def test_trigonometry(expression: str, angle_mode: str, expected: float) -> None:
    result = calculator(expression, angle_mode=angle_mode)  # type: ignore[arg-type]
    assert result == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("pi", math.pi),
        ("2*pi", 2 * math.pi),
        ("e", math.e),
        ("e**2", math.e**2),
        ("tau", math.tau),
        ("tau/2", math.pi),
        ("inf + 1", math.inf),
        ("1/inf", 0),
        ("1e3", 1000),
        ("1.5e-2", 0.015),
        ("2E+4", 20000),
        ("1e3 + 1", 1001),
        ("1_000 + 2_000", 3000),
        ("1_000_000 * 2", 2000000),
        (".5 + .5", 1),
    ],
)
def test_constants_and_numbers(expression: str, expected: float | int) -> None:
    assert calculator(expression) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize(
    ("expression", "variables", "expected"),
    [
        ("x + y", {"x": 10, "y": 5}, 15),
        ("x * 2", {"x": 3.5}, 7),
        ("x**2 + y**2", {"x": 3, "y": 4}, 25),
        ("a*b + c", {"a": 2, "b": 3, "c": 1}, 7),
        ("x = 2; x * 3", {}, 6),
        ("a = 1; b = a + 2; a + b", {}, 4),
        ("pi", {"pi": 123}, math.pi),
    ],
)
def test_variables_and_assignments(
    expression: str, variables: dict[str, float | int], expected: float | int
) -> None:
    result = calculator(expression, variables=variables)
    assert result == pytest.approx(expected, rel=1e-9)
    if expression.startswith("x ="):
        assert variables == {}


@pytest.mark.parametrize(
    ("expression", "precision", "expected"),
    [
        ("10/3", None, 10 / 3),
        ("10/3", 2, 3.33),
        ("pi", 4, 3.1416),
        ("sqrt(2)", 3, 1.414),
    ],
)
def test_precision(expression: str, precision: int | None, expected: float) -> None:
    result = calculator(expression, precision=precision)
    assert result == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1+2+3+4+5+6+7+8+9+10", 55),
        ("1*2*3*4*5*6*7*8*9*10", 3628800),
        ("1+2+3+4+5*6*7*8*9*10*12*0+2/2+3", 14),
        ("sqrt(3**2 + 4**2)", 5),
        ("log(e**2)", 2),
        ("factorial(5) + factorial(3)", 126),
        ("max(1,2,3) * min(4,5,6) + sqrt(16)", 16),
    ],
)
def test_composed_expressions(expression: str, expected: float | int) -> None:
    assert calculator(expression) == pytest.approx(expected, rel=1e-9)


def test_verbose_logs(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("INFO"):
        assert calculator("2+3", verbose=True) == 5
    assert "2 + 3 -> 5" in caplog.text


@pytest.mark.parametrize(
    ("expression", "exception"),
    [
        ("", ValueError),
        ("   ", ValueError),
        ("2 + @", TokenizeError),
        ("(2+3", ParseError),
        ("2+3)", ParseError),
        ("z + 1", EvaluationError),
        ("foo(1)", EvaluationError),
        ("sqrt(1, 2)", ParseError),
        ("min()", ParseError),
        ("max()", ParseError),
        ("1/0", ZeroDivisionError),
        ("1//0", ZeroDivisionError),
        ("1%0", ZeroDivisionError),
        ("sqrt(-1)", EvaluationError),
        ("log(0)", EvaluationError),
        ("log(-1)", EvaluationError),
        ("factorial(-1)", EvaluationError),
        ("factorial(3.5)", EvaluationError),
        ("inf - inf", EvaluationError),
        ("1e", TokenizeError),
    ],
)
def test_errors(expression: str, exception: type[Exception]) -> None:
    with pytest.raises(exception):
        calculator(expression)


def test_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        calculator("1", angle_mode="grad")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        calculator("1", precision=-1)
