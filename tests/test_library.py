import pytest

from example_package import greet


def test_greet_returns_greeting() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_strips_whitespace() -> None:
    assert greet("  Ada ") == "Hello, Ada!"


@pytest.mark.parametrize("name", ["", "   "])
def test_greet_rejects_empty_name(name: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        greet(name)
