# tpl-python-core

[English README](./README.md)

`tpl-python-core` 是一个基于 Copier 的 Python 项目模板仓库，目标是尽量贴近
`pyfcstm` / `pyudbm` / `hbutils` 这套现有项目的基础设施和使用习惯。

生成出来的仓库默认包含：

- 基于 `setup.py` 的打包元数据
- `requirements.txt` 以及 `requirements-*.txt` extras 自动发现
- `AGENTS.md`，以及指向它的 `CLAUDE.md` 软链接
- Sphinx + Read the Docs 文档骨架
- 自动 API RST 生成脚本
- GitHub Actions 的测试与发布工作流

可选能力：

- PyInstaller 构建脚手架，以及对应的 CLI 入口布局
- 基于 gist 的 LOC badge 自动更新

## 生成新仓库

从本地模板直接生成：

```bash
copier copy --trust /path/to/tpl-python-core /path/to/new-project
```

模板发布到 GitHub 后，也可以直接这样生成：

```bash
copier copy --trust gh:HansBug/tpl-python-core /path/to/new-project
```

生成后的仓库默认应支持：

- `make bootstrap`
- `make unittest`
- `make docs`
- `make package`
- `make build`（启用 PyInstaller 时）

## 生成仓库内置 CI

生成仓库自带：

- `test.yml`：跨平台单元测试
- `release.yml`：dry-run 打包校验与正式发布
- `badge.yml`：启用时用于刷新 LOC badge

通常只需要按需配置可选 secrets：

- `CODECOV_TOKEN`：覆盖率上传
- `PYPI_PASSWORD`：发布到 PyPI
- `BADGE_GIST_TOKEN`：刷新可选 LOC badge

## 模板本地开发

```bash
python -m pip install -r requirements-dev.txt
python scripts/smoke_copy.py --fixture tests/fixtures/minimal.yml
python scripts/smoke_copy.py --fixture tests/fixtures/loc_badge.yml
python scripts/smoke_copy.py --fixture tests/fixtures/cli_pyinstaller.yml
```

模板仓库自身也带有 GitHub Actions smoke matrix，会在 `ubuntu-22.04` 和
`macos-14` 上分别验证这两个 fixture。

## Git Tag

Copier 的更新能力更适合搭配 Git tag 一起使用：

```bash
git tag v0.1.0
git push origin v0.1.0
```
