"""Core logic. It never prints or exits, so any front end can reuse it."""


def greet(name: str) -> str:
    """Return a greeting for ``name``.

    Raises:
        ValueError: If ``name`` is empty or only whitespace.
    """
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must not be empty")
    return f"Hello, {cleaned}!"
