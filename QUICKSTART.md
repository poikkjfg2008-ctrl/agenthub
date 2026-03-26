# Quickstart（5 分钟）

## 1) 环境要求

- Python 3.12+
- Node.js 22+
- OpenCode（默认 `http://127.0.0.1:4096`）
- OpenWork（默认 `http://127.0.0.1:8787`，可选）

---

## 2) 一键启动（推荐）

```bash
./scripts/start.sh
```

脚本会：
1. 检查 Python / Node
2. 安装依赖（若缺失）
3. 启动 FastAPI（8000）
4. 启动 Vite（5173）
5. 写入日志到 `logs/`

停止：

```bash
./scripts/stop.sh
```

---

## 3) 手动启动

### 后端
```bash
cd backend
/home/yy/python312/bin/python -m pip install -r requirements.txt
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

---

## 4) 首次访问与登录

访问：`http://localhost:5173`

前端会调用 `/api/auth/me`；若未登录，会跳转到：

```text
/api/auth/mock-login?emp_no=E10001
```

该接口会写入 `access_token` Cookie，并返回登录结果 JSON。

---

## 5) 快速自检（API）

> 以下命令在服务已启动的情况下执行。

```bash
# 健康检查
curl http://localhost:8000/api/health

# mock 登录（保存 cookie）
curl "http://localhost:8000/api/auth/mock-login?emp_no=E10001" -c cookies.txt

# 当前用户
curl http://localhost:8000/api/auth/me -b cookies.txt

# 资源列表
curl http://localhost:8000/api/resources -b cookies.txt

# 启动一个 native 资源
curl -X POST http://localhost:8000/api/resources/general-chat/launch -b cookies.txt
```

---

## 6) 常见问题

### Q1: 启动 resource 时报 OpenCode 错误
确认 OpenCode 服务地址与认证匹配：
- `OPENCODE_BASE_URL`
- `OPENCODE_USERNAME`
- `OPENCODE_PASSWORD`

### Q2: WebSDK 资源白屏
优先检查：
1. `/api/launches/{launch_id}/embed-config` 是否返回 `script_url/app_key/base_url`
2. `public/sdk-host.html` 中 SDK 是否加载成功
3. 第三方 SDK 域名是否可访问

### Q3: Redis 是否必须
不是。默认 `USE_REDIS=false` 使用内存存储，便于本地联调。
