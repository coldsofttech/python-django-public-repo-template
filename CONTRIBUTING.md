# Contributing

Thanks for taking the time to contribute! By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting bugs and requesting features

Open an issue using one of the provided forms. Search existing issues first. For security problems, do **not** open an issue; follow [SECURITY.md](SECURITY.md).

## Submitting changes

1. Fork the repository and create a branch from `main`.
2. Make your change, keeping it focused on one thing.
3. Set up with [uv](https://docs.astral.sh/uv/): `uv sync`, then `uv run pre-commit install --hook-type pre-commit --hook-type post-commit`.
4. Run `uv run pytest`, `uv run ruff check .` and `uv run mypy` before you push.
5. Add an entry under `[Unreleased]` in `CHANGELOG.md` (one or two lines, written from a reader's point of view).
6. Open a pull request and fill in the template.

## Pull request rules

- `main` is protected: changes land through pull requests that are squash-merged.
- Required checks must pass and the branch must be up to date.
- A code owner must review, and all conversations must be resolved.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/), for example `fix: handle empty input`.
