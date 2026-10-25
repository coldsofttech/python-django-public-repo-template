import example_package


def test_version_is_defined() -> None:
    assert isinstance(example_package.__version__, str)
