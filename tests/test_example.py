import pytest

from abx_example import greet


def test_greet_returns_a_greeting() -> None:
    assert greet("Alex") == "Hello, Alex!"


def test_greet_rejects_an_empty_name() -> None:
    with pytest.raises(ValueError):
        greet("  ")
