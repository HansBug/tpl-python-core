import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from copier import run_copy


def _run(cmd, cwd, env=None):
    print(f"+ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def _load_answers(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _assert_rendered_layout(project_dir: Path, answers: dict):
    claude = project_dir / "CLAUDE.md"
    agents = project_dir / "AGENTS.md"
    shims_dir = project_dir / "docs" / "source" / "_shims"
    assert agents.is_file(), "AGENTS.md should exist."
    assert claude.is_symlink(), "CLAUDE.md should be a symlink."
    assert os.readlink(claude) == "AGENTS.md", "CLAUDE.md should point to AGENTS.md."
    assert (shims_dir / ".keep").is_file()

    assert (project_dir / "test" / "config" / "test_meta.py").is_file()
    assert (project_dir / "test" / "test_core.py").is_file()

    package_name = answers["package_name"]
    if answers.get("with_pyinstaller"):
        assert (project_dir / package_name / "__main__.py").is_file()
        assert (project_dir / package_name / "entry").is_dir()
        assert (project_dir / "test" / "entry" / "test_cli.py").is_file()
        assert (project_dir / "requirements-build.txt").is_file()
        assert (project_dir / "tools" / "generate_spec.py").is_file()
        assert (shims_dir / answers["cli_command"]).is_file()
    else:
        assert not (project_dir / package_name / "__main__.py").exists()
        assert not (project_dir / package_name / "entry").exists()
        assert not (project_dir / "test" / "entry").exists()
        assert not (project_dir / "requirements-build.txt").exists()
        assert not (project_dir / "tools" / "generate_spec.py").exists()
        assert sorted(path.name for path in shims_dir.iterdir()) == [".keep"]


def main():
    parser = argparse.ArgumentParser(description="Render and validate tpl-python-core smoke projects.")
    parser.add_argument("--fixture", required=True, help="Fixture YAML file with Copier answers.")
    parser.add_argument("--template", default=None, help="Template repo path. Defaults to current repo root.")
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep the generated smoke directory instead of deleting it.",
    )
    args = parser.parse_args()

    fixture_path = Path(args.fixture).resolve()
    template_root = Path(args.template).resolve() if args.template else Path(__file__).resolve().parents[1]
    answers = _load_answers(fixture_path)

    with tempfile.TemporaryDirectory(prefix="tpl-python-core-smoke-") as tmpdir:
        tmp_path = Path(tmpdir)
        project_dir = tmp_path / answers["repo_name"]
        venv_dir = tmp_path / ".venv"

        run_copy(
            str(template_root),
            str(project_dir),
            data=answers,
            defaults=True,
            overwrite=True,
            unsafe=True,
        )
        _assert_rendered_layout(project_dir, answers)

        _run([sys.executable, "-m", "venv", str(venv_dir)], cwd=tmp_path)
        py = _venv_python(venv_dir)

        env = dict(os.environ)
        env["PATH"] = f"{py.parent}:{env.get('PATH', '')}"

        _run([str(py), "-m", "pip", "install", "--upgrade", "pip"], cwd=project_dir, env=env)
        _run([str(py), "-m", "pip", "install", "build"], cwd=project_dir, env=env)
        _run(["make", "bootstrap"], cwd=project_dir, env=env)
        _run(["make", "unittest"], cwd=project_dir, env=env)
        _run(["make", "docs"], cwd=project_dir, env=env)
        _run(["make", "package"], cwd=project_dir, env=env)
        if answers.get("with_pyinstaller"):
            _run(["make", "build"], cwd=project_dir, env=env)

        if args.keep:
            keep_dir = template_root / ".smoke" / answers["repo_name"]
            if keep_dir.exists():
                shutil.rmtree(keep_dir)
            keep_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(project_dir, keep_dir, symlinks=True)
            print(f"Kept smoke output at {keep_dir}")


if __name__ == "__main__":
    main()
