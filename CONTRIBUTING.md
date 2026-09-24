# Contributing

Bug reports, ideas and pull requests are welcome, in English or Spanish.

## Reporting a bug or proposing an idea

Open an [issue](https://github.com/SergeyShk/esTS/issues/new/choose) using a template. A bug report needs a minimal code example with the text that reproduces it, the expected and actual behaviour, and the versions of esTS, Python and the OS. A proposal needs the statistic or tool you want and the source (paper, library) it relies on: the library follows published definitions, not formulas of its own.

## Development environment

The project uses [uv](https://docs.astral.sh/uv/) for dependencies and [ruff](https://docs.astral.sh/ruff/) for linting and formatting. Python 3.11 or newer is required.

```bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS

make deps                   # create the environment and install all dependencies
uv run pre-commit install   # hooks: linters on commit, tests on push
```

The full list of commands is in `make help`.

## Checks

Before submitting a pull request, these must pass:

```bash
make lint        # ruff check, ruff format --check, mypy
make test        # pytest: tests and docstring examples (doctest)
make docs-build  # mkdocs build --strict, if the documentation changed
```

CI runs the same on Python 3.11-3.14 (Linux) and on Windows and macOS for one Python version. Tests marked `network` download data; they can be skipped locally with `uv run pytest -m "not network"`.

## What a pull request is expected to contain

- **One topic per pull request.** Unrelated changes go separately.
- **Tests.** New code is covered by tests in `tests/` (mirroring the package), coverage stays at 90% or above. The values of new metrics are checked against an example computed by hand or against a reference implementation (textstat, quanteda, stylo, NLTK, rantanplan and the like).
- **Documentation.** Every module has a page in `docs/`; the documentation is bilingual - the English page `docs/*.md` and the Spanish page `docs/*.es.md` next to it, and `tests/test_docs.py` checks that their sections, anchors and links match. README changes go into both `README.md` and `README.es.md`. Examples in docstrings and documentation show the actual output.
- **Sources.** A new statistic cites the source of its formula in the docstring and on the documentation page; the implementation is checked against it, and differences from other libraries are stated explicitly.
- **Compatibility.** Changes to the behaviour of existing statistics or signatures come with an explanation in the pull request description: it goes into the release notes.
- **Style.** Code is formatted with ruff (`make format`), types are checked with mypy, docstrings are in English in the project format (`Description`, `Arguments`, `Returns`, `Raises`). Comments do not repeat what the code already says.
- **Commits.** Messages in English, imperative mood: "Add ...", "Fix ...", "Remove ...".

The pull request description answers two questions: what was done and why. If it closes an issue, mention its number.

## Repository layout

- `ests/` - the package.
- `tests/` - tests mirroring the package; `tests/test_docs.py` keeps the two documentation languages in sync.
- `docs/` - MkDocs (Material) documentation, `mkdocs.yml` - navigation and its Spanish translation.
- `.github/workflows/` - CI (`ci.yml`), publishing (`publish.yml`), documentation (`docs.yml`).

The version lives only in `pyproject.toml`; releases are made through GitHub Releases, changes are described in the release notes, there is no separate CHANGELOG file.
