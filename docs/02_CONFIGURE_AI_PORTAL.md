# AI Portal 配置指南

本文档介绍如何根据已启动的 OpenCode 和 OpenWork 服务配置 AI Portal 项目。

---

## 一、配置文件位置

AI Portal 的主要配置文件：

```
agenthub/
├── backend/
│   ├── .env                    # 后端环境变量配置（从此文件创建）
│   └── config/
│       └── resources.json      # 资源目录配置
├── frontend/
│   └── .env                    # 前端环境变量配置（可选）
└── .env.example                # 配置示例文件
```

---

## 二、后端配置（backend/.env）

### 2.1 创建配置文件

```bash
cd /path/to/agenthub
cp .env.example backend/.env
```

### 2.2 配置项说明

编辑 `backend/.env` 文件：

```bash
# ============= 服务器配置 =============
PORT=8000
HOST=0.0.0.0
RELOAD=false                    # 生产环境设为 false，避免事件循环问题

# ============= 存储配置 =============
# 使用内存存储（开发环境，无需 Docker）
USE_REDIS=false

# 或使用 Redis 存储（生产环境）
# USE_REDIS=true
# REDIS_URL=redis://localhost:6379/0

# ============= JWT 配置 =============
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# 开发环境：认证失败时回退到 mock 用户
AUTH_MOCK_FALLBACK_ENABLED=true

# ============= OpenCode 配置 =============
# 根据实际启动的 OpenCode 地址配置
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENCODE_USERNAME=opencode
OPENCODE_PASSWORD=              # 如果不需要密码，留空

# ============= OpenWork 配置 =============
# 根据实际启动的 OpenWork 地址配置
OPENWORK_BASE_URL=http://127.0.0.1:8787
OPENWORK_TOKEN=your-openwork-token  # 如果有认证令牌

# ============= Portal 配置 =============
PORTAL_NAME=AI Portal
RESOURCES_PATH=config/resources.json

# ============= 日志配置 =============
LOG_LEVEL=INFO
# LOG_LEVEL=DEBUG  # 开发时使用 DEBUG 级别

# ============= CORS 配置 =============
# 生产环境添加实际域名
CORS_ORIGINS=http://localhost:5173,http://localhost:8000
```

### 2.3 配置检查清单

| 配置项 | 检查点 | 示例值 |
|--------|--------|--------|
| OPENCODE_BASE_URL | 确认 OpenCode 实际地址 | http://127.0.0.1:4096 |
| OPENWORK_BASE_URL | 确认 OpenWork 实际地址 | http://127.0.0.1:8787 |
| OPENCODE_PASSWORD | 无密码时留空，不要设默认值 | （空） |
| RELOAD | 生产环境设为 false | false |

---

## 三、资源配置（resources.json）

### 3.1 文件位置

```
backend/config/resources.json
```

### 3.2 配置结构说明

```json
[
  {
    "id": "唯一标识",
    "name": "显示名称",
    "type": "资源类型",
    "launch_mode": "启动模式",
    "group": "分组名称",
    "description": "描述",
    "enabled": true,
    "tags": ["标签"],
    "config": {
      // 类型特定的配置
    }
  }
]
```

### 3.3 资源类型说明

| 类型 | 说明 | launch_mode |
|------|------|-------------|
| `direct_chat` | 通用对话 | native |
| `skill_chat` | Skill 对话 | native |
| `kb_websdk` | 知识库 WebSDK | websdk |
| `agent_websdk` | 智能应用 WebSDK | websdk |

---

## 四、前端配置（可选）

### 4.1 创建前端配置文件

```bash
cd /path/to/agenthub/frontend
cp .env.example .env  # 如果不存在则直接创建
```

### 4.2 配置项

```bash
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 应用名称
VITE_APP_NAME=AI Portal
```

### 4.3 默认行为

如果不配置前端 `.env`，前端会使用相对路径 `/` 自动访问后端，适用于前后端同域部署。

---

## 五、配置验证

### 5.1 前置检查脚本

AI Portal 提供了前置检查脚本，验证 OpenCode/OpenWork 连接：

```bash
# 进入项目目录
cd /path/to/agenthub

# 执行前置检查
python3 scripts/preflight_check.py
```

**预期输出**:
```
🔍 启动前置检查（OpenCode/OpenWork/WebSDK）
1. ✅ opencode_base: http://127.0.0.1:4096 (127.0.0.1:4096)
2. ✅ openwork_base: http://127.0.0.1:8787 (127.0.0.1:8787)
...
✅ 前置检查通过。
```

### 5.2 手动验证

```bash
# 验证 OpenCode
curl http://127.0.0.1:4096

# 验证 OpenWork
curl http://127.0.0.1:8787

# 验证 AI Portal 配置
cd backend
/home/yy/python312/bin/python -c "from app.config import settings; print(f'OpenCode: {settings.opencode_base_url}')"
```

---

## 六、启动 AI Portal

### 6.1 一键启动

```bash
cd /path/to/agenthub
./scripts/start.sh
```

### 6.2 启动流程说明

```
start.sh 执行流程:
1. 检查 Python/Node 环境
2. 执行 preflight_check.py（检查 OpenCode/OpenWork）
3. 安装依赖（如果需要）
4. 启动 FastAPI 后端 (端口 8000)
5. 启动 Vite 前端 (端口 5173)
6. 输出访问地址
```

### 6.3 访问服务

| 服务 | URL |
|------|-----|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

---

## 七、常见配置问题

### 7.1 前置检查失败

**问题**: `❌ opencode_base: Connection refused`

**解决**:
```bash
# 检查 OpenCode 是否运行
curl http://127.0.0.1:4096

# 如果未运行，启动 OpenCode
cd /path/to/opencode
python -m opencode --port 4096
```

### 7.2 认证失败

**问题**: 访问 API 返回 401

**解决**:
```bash
# 检查 .env 中是否启用 mock fallback
AUTH_MOCK_FALLBACK_ENABLED=true
```

### 7.3 CORS 错误

**问题**: 浏览器报跨域错误

**解决**:
```bash
# 在 backend/.env 中添加前端地址
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-domain.com
```

### 7.4 消息发送 500 错误

**问题**: 发送消息返回 500

**解决**:
```bash
# 确保 RELOAD=false
# 重启服务
./scripts/stop.sh
./scripts/start.sh
```

---

## 八、生产环境配置

### 8.1 安全加固

```bash
# backend/.env
RELOAD=false
AUTH_MOCK_FALLBACK_ENABLED=false
JWT_SECRET=your-very-strong-random-secret-key
OPENCODE_PASSWORD=your-opencode-password
```

### 8.2 使用 Redis

```bash
# backend/.env
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
```

启动 Redis:
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

### 8.3 反向代理配置（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 九、配置变更后的重启

```bash
# 修改 .env 或 resources.json 后需要重启

# 方式1: 使用脚本
./scripts/stop.sh
./scripts/start.sh

# 方式2: 手动重启后端
kill <backend_pid>
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 相关文档

- [01_START_OPENCODE_OPENWORK.md](./01_START_OPENCODE_OPENWORK.md) - OpenCode/OpenWork 启动指南
- [03_ADD_WEBSDK_RESOURCES.md](./03_ADD_WEBSDK_RESOURCES.md) - WebSDK 资源配置
- [WEBSDK_EMBEDDING_GUIDE.md](../WEBSDK_EMBEDDING_GUIDE.md) - WebSDK 嵌入详细指南
