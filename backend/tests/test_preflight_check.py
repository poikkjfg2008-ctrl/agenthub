"""preflight_check 脚本测试（配置解析层）。"""

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "preflight_check.py"


def run_command(args):
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_preflight_parse_only_should_pass():
    result = run_command([sys.executable, str(SCRIPT_PATH), "--no-network"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "前置检查通过" in result.stdout
    assert "opencode_base" in result.stdout
    assert "openwork_base" in result.stdout


def test_preflight_with_custom_repo_root_should_pass():
    result = run_command(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--no-network",
            "--repo-root",
            str(REPO_ROOT),
        ]
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "resources 文件" in result.stdout


def test_preflight_should_use_resources_path_from_env(tmp_path):
    backend_dir = tmp_path / "backend"
    custom_resources_dir = backend_dir / "custom"
    backend_dir.mkdir()
    custom_resources_dir.mkdir()

    (backend_dir / ".env").write_text("RESOURCES_PATH=custom/resources.json\n", encoding="utf-8")
    (custom_resources_dir / "resources.json").write_text("[]", encoding="utf-8")

    result = run_command(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--no-network",
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert str(custom_resources_dir / "resources.json") in result.stdout
