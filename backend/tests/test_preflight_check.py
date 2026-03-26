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
