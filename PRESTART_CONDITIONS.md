# 启动前置条件文档（OpenCode / OpenWork / 端口连通）

> 适用场景：本仓库在调用「原生对话、Skill 对话、知识库 WebSDK、智能应用 WebSDK」前，必须先确保 OpenCode / OpenWork 已运行，并且端口与服务端点可达。

## 1. 必须先启动的外部服务

| 服务 | 默认地址 | 默认端口 | 用途 |
|---|---|---:|---|
| OpenCode | `http://127.0.0.1:4096` | 4096 | 原生/Skill 对话、WebSDK 脚本和知识库/智能应用端点 |
| OpenWork | `http://127.0.0.1:8787` | 8787 | Skill 安装状态与引擎 reload 能力 |

> 地址来源：`backend/.env`（若未配置则使用默认值）。

## 2. 推荐启动顺序

1. 启动 OpenCode（确保 API 与 WebSDK 静态资源可访问）。
2. 启动 OpenWork（确保技能状态接口可访问）。
3. 执行本仓库前置检查（`scripts/preflight_check.py`）。
4. 再启动 Portal（`./scripts/start.sh`）。

## 3. 启动前自动检查（已集成）

`./scripts/start.sh` 在启动后端/前端前，会自动执行：

```bash
python3 scripts/preflight_check.py
```

检查内容：
- `backend/.env` 中的 `OPENCODE_BASE_URL` / `OPENWORK_BASE_URL`。
- `backend/config/resources.json` 中所有 WebSDK 资源的 `script_url` / `base_url`。
- 每个 URL 的 host/port 解析是否有效。
- 默认执行 socket 连通性检查（TCP 可连）。

失败时 `start.sh` 会直接中止，避免进入“前端启动了但对话不可用”的状态。

## 4. 手动执行前置检查

### 4.1 完整连通性检查（本地联调）

```bash
python3 scripts/preflight_check.py
```

### 4.2 仅检查配置格式（CI/离线环境）

```bash
python scripts/preflight_check.py --no-network
```

## 5. 联调测试清单（启动前置条件）

### 5.1 配置解析测试（自动化）

```bash
cd backend
python -m pytest tests/test_preflight_check.py
```

覆盖点：
- 前置脚本在 `--no-network` 下可正常解析 `.env` 与 `resources.json`。
- 输出包含 OpenCode/OpenWork 关键端点。

### 5.2 运行态连通性测试（手工）

```bash
# OpenCode
curl -i http://127.0.0.1:4096

# OpenWork
curl -i http://127.0.0.1:8787

# Portal 健康检查（前置通过后启动 Portal）
curl -s http://localhost:8000/api/health
```

## 6. 常见失败与修复

### 6.1 `Connection refused`
- 对应服务未启动或端口错误。
- 修复：确认 OpenCode/OpenWork 进程与 `backend/.env` 一致。

### 6.2 URL 非法（例如缺少协议头）
- `resources.json` 中 `script_url` / `base_url` 配置不完整。
- 修复：统一使用 `http://` 或 `https://` 完整 URL。

### 6.3 只想本地改配置，不希望阻断启动
- 先使用 `--no-network` 校验配置，再单独排查网络。
- 生产/联调建议保留网络检查，减少运行期故障。
