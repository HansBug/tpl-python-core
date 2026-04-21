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
            unsafe=False,
        )

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
            shutil.copytree(project_dir, keep_dir)
            print(f"Kept smoke output at {keep_dir}")


if __name__ == "__main__":
    main()
