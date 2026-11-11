"""Small package used to demonstrate the release tooling."""

from typing_extensions import TypeAlias

Greeting: TypeAlias = str


def greet(name: str) -> Greeting:
    """Return a greeting for name."""
    if not name.strip():
        raise ValueError("name must not be empty")
    return f"Hello, {name}!"
