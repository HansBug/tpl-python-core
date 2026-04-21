# tpl-python-core

[中文说明 / Chinese README](./README_zh.md)

`tpl-python-core` is a Copier template for Python repositories that should feel
close to the existing `pyfcstm` / `pyudbm` / `hbutils` house style.

The generated repositories always include:

- Python package layout with `setup.py`-driven metadata
- `requirements.txt` plus `requirements-*.txt` extras discovery
- `AGENTS.md` and `CLAUDE.md`
- Sphinx + Read the Docs documentation skeleton
- auto-generated API RST helpers
- GitHub Actions workflows for test, docs, and release

Optional features:

- CLI scaffold
- PyInstaller build scaffold

## Create A Repository

Render a new project from the local template:

```bash
copier copy /path/to/tpl-python-core /path/to/new-project
```

After the template repo is published, the remote form is:

```bash
copier copy gh:HansBug/tpl-python-core /path/to/new-project
```

The generated repository is expected to support:

- `make bootstrap`
- `make unittest`
- `make docs`
- `make package`
- `make build` when PyInstaller is enabled

## Generated CI

Generated repositories include:

- `test.yml` for cross-platform unit test runs
- `docs.yml` for docs build validation
- `release.yml` for PyPI and release asset publishing

Only optional secrets should need to be configured:

- `CODECOV_TOKEN` for coverage upload
- `PYPI_PASSWORD` for release publishing

## Local Template Development

```bash
python -m pip install -r requirements-dev.txt
python scripts/smoke_copy.py --fixture tests/fixtures/minimal.yml
python scripts/smoke_copy.py --fixture tests/fixtures/cli_pyinstaller.yml
```

The template repo also has a GitHub Actions smoke matrix on `ubuntu-22.04` and
`macos-14` for both fixtures.

## Git Tagging

Copier updates work best when the template repo is versioned with Git tags:

```bash
git tag v0.1.0
git push origin v0.1.0
```
