# python-public-repo-template

[![CI](https://github.com/coldsofttech/python-public-repo-template/actions/workflows/ci.yml/badge.svg)](https://github.com/coldsofttech/python-public-repo-template/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/python-public-repo-template)](https://pypi.org/project/python-public-repo-template/)
[![Python versions](https://img.shields.io/pypi/pyversions/python-public-repo-template)](https://pypi.org/project/python-public-repo-template/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/coldsofttech/python-public-repo-template)](LICENSE)

A ready-to-use starting point for public Python projects on GitHub. It includes a typed package layout, automated testing on Python 3.11 to 3.15, linting, one-step releases to PyPI, and the community and security files a public repository needs.

## What you get

- A typed `src` package with tests and a coverage minimum
- Fast, reproducible setup with [uv](https://docs.astral.sh/uv/)
- Linting, formatting and type checking before every commit and in CI
- Automated tests on Python 3.11 to 3.15 (Ubuntu) and 3.11 (Windows and macOS)
- Publishing to PyPI when you create a GitHub release, with no stored tokens
- Contribution, conduct, support and security-reporting guidelines
- Issue forms, a pull request template and automated dependency updates

## Getting started

1. Click **Use this template** on GitHub and create your new repository.
2. Run the **Init** workflow from the Actions tab and merge the pull request it opens. This fills in your owner and repository name.
3. Rename the example package and set your project description. See the [development guide](docs/development.md).
4. Add your contact details in `CODE_OF_CONDUCT.md`, delete `.github/workflows/init.yml`, and replace this description.
5. Apply the repository protections by following the [setup guide](docs/repo-setup.md).
6. Install dependencies and commit checks:

   ```bash
   uv sync
   uv run pre-commit install --hook-type pre-commit --hook-type post-commit
   ```

## Installation

Requires Python 3.11 or newer.

```bash
pip install python-public-repo-template
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add python-public-repo-template
```

To install the latest development version from source:

```bash
pip install git+https://github.com/coldsofttech/python-public-repo-template.git
```

## Usage

```python
import example_package

print(example_package.__version__)
```

> After renaming the example package, update the import above. Once you have written your project's real API, replace this example with a short walkthrough of it.

## Development

```bash
git clone https://github.com/coldsofttech/python-public-repo-template.git
cd python-public-repo-template
uv sync
uv run pytest
```

See the [development guide](docs/development.md) for linting, type checking and releasing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).
