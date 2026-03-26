#!/usr/bin/env python3
"""启动前置检查：验证 OpenCode/OpenWork 及 WebSDK 端点连通性。"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
from urllib.parse import urlparse

DEFAULTS = {
    "OPENCODE_BASE_URL": "http://127.0.0.1:4096",
    "OPENWORK_BASE_URL": "http://127.0.0.1:8787",
    "RESOURCES_PATH": "config/resources.json",
}


def parse_env(env_path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not env_path.exists():
        return values

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def socket_check(host: str, port: int, timeout: float = 2.5) -> Tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "ok"
    except OSError as exc:
        return False, str(exc)


def normalize_endpoint(url: str) -> Tuple[str, str, int]:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise ValueError(f"无效 URL: {url}")
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"仅支持 http/https URL: {url}")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return parsed.geturl(), parsed.hostname, port


def collect_endpoints(resources_path: Path, env_values: Dict[str, str]) -> List[Tuple[str, str]]:
    endpoints: List[Tuple[str, str]] = []

    opencode = env_values.get("OPENCODE_BASE_URL", DEFAULTS["OPENCODE_BASE_URL"])
    openwork = env_values.get("OPENWORK_BASE_URL", DEFAULTS["OPENWORK_BASE_URL"])

    endpoints.append(("opencode_base", opencode))
    endpoints.append(("openwork_base", openwork))

    if resources_path.exists():
        resources = json.loads(resources_path.read_text(encoding="utf-8"))
        for item in resources:
            cfg = item.get("config", {})
            resource_id = item.get("id", "unknown")
            for key in ("script_url", "base_url"):
                value = cfg.get(key)
                if value:
                    endpoints.append((f"{resource_id}.{key}", value))

    return endpoints


def resolve_resources_path(repo_root: Path, env_values: Dict[str, str]) -> Path:
    backend_root = repo_root / "backend"
    raw_path = env_values.get("RESOURCES_PATH", DEFAULTS["RESOURCES_PATH"]).strip()
    normalized_path = raw_path.strip('"').strip("'")
    resources_path = Path(normalized_path).expanduser()

    if resources_path.is_absolute():
        return resources_path

    return backend_root / resources_path


def dedupe_endpoints(endpoints: Iterable[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen: Set[str] = set()
    result: List[Tuple[str, str]] = []
    for name, url in endpoints:
        if url in seen:
            continue
        seen.add(url)
        result.append((name, url))
    return result


def run_preflight(repo_root: Path, check_network: bool) -> int:
    env_path = repo_root / "backend" / ".env"
    env_values = parse_env(env_path)
    resources_path = resolve_resources_path(repo_root, env_values)
    endpoints = dedupe_endpoints(collect_endpoints(resources_path, env_values))

    print("🔍 启动前置检查（OpenCode/OpenWork/WebSDK）")
    print(f"- env 文件: {env_path}")
    print(f"- resources 文件: {resources_path}")
    print(f"- 检查模式: {'网络连通性' if check_network else '配置解析'}")

    failed = False
    for idx, (name, url) in enumerate(endpoints, start=1):
        try:
            normalized, host, port = normalize_endpoint(url)
        except ValueError as exc:
            print(f"{idx}. ❌ {name}: {exc}")
            failed = True
            continue

        if not check_network:
            print(f"{idx}. ✅ {name}: {normalized} -> {host}:{port}")
            continue

        ok, message = socket_check(host, port)
        if ok:
            print(f"{idx}. ✅ {name}: {normalized} ({host}:{port})")
        else:
            print(f"{idx}. ❌ {name}: {normalized} ({host}:{port}) - {message}")
            failed = True

    if failed:
        print("\n❌ 前置检查失败：请先启动依赖服务并确认端点可访问，再执行 start。")
        return 1

    print("\n✅ 前置检查通过。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Portal 启动前置检查")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="仓库根目录（默认自动推断）",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="仅检查配置解析，不做端口连通性检查（用于 CI/单元测试）",
    )
    args = parser.parse_args()

    return run_preflight(Path(args.repo_root), check_network=not args.no_network)


if __name__ == "__main__":
    sys.exit(main())
