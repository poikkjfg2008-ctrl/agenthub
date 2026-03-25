# AI Portal - 统一入口

AI Portal 是一个为企业内部 R&D 用户设计的统一 AI 资源入口。它提供了一个集中的访问点，用于访问多种 AI 服务，包括原生对话、基于技能的对话、知识库和传统 Agent 应用。

## 目录

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [开发指南](#开发指南)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [常见问题](#常见问题)

## 功能特性

### ✅ 已实现功能

- **统一资源入口**: 浏览和访问所有 AI 资源
- **模拟 SSO 登录**: 基于员工号的快速登录（真实 SSO 集成接口已预留）
- **资源目录**: 按类别分组的资源浏览
- **技能商店**: 浏览、权限检查和启动技能
- **原生对话**: 通过 OpenCode HTTP API 的直接对话
- **技能对话**: 基于技能的对话，注入系统提示
- **WebSDK 知识库**: 通过 iframe 嵌入集成知识库
- **WebSDK Agent 应用**: 集成传统 Agent 应用
- **会话管理**: 原生/技能会话的历史记录和持久化
- **启动记录**: WebSDK 应用的启动追踪
- **内存存储**: 无需 Docker 的内置内存存储
- **JSON 日志**: 包含 trace_id 的结构化日志，便于调试

### 🎯 计划功能 (V2+)

- 真实 SSO 集成 (SAML/OAuth)
- 技能在线编辑器
- WebSDK 应用会话历史集成
- 知识库管理后端
- 多技能组合
- 复杂审批流程

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Mock SSO / Future Real SSO              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Portal WebUI                         │
│  - Resource browser  - Chat interface  - Session sidebar     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI BFF / Gateway (Python)                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Auth (mock now, real SSO later)                   │    │
│  │  Resource Catalog & ACL                            │    │
│  │  Session Center (native/skill only)                │    │
│  │  Launch Record Center (websdk apps)                │    │
│  │  Trace Middleware & JSON Logging                   │    │
│  └────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Execution Adapters                        │    │
│  │  ┌────────────────┐  ┌────────────────┐            │    │
│  │  │OpenCodeAdapter │  │SkillChatAdapter│            │    │
│  │  └────────────────┘  └────────────────┘            │    │
│  │  ┌────────────────┐  ┌────────────────┐            │    │
│  │  │WebSDKAdapter   │  │OpenWorkAdapter │            │    │
│  │  └────────────────┘  └────────────────┘            │    │
│  └────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Storage Layer                             │    │
│  │  - Memory Store (default, no Docker)                │    │
│  │  - Redis Store (optional, requires Docker)          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│  OpenCode    │    │  OpenWork    │    │  WebSDK Apps     │
│  Server      │    │  Server      │    │  (KB + Legacy)   │
│  (port 4096) │    │  (port 8787) │    │  (iframe embed)  │
└──────────────┘    └──────────────┘    └──────────────────┘
```

## 技术栈

### 后端
- **Python 3.12**: 主要开发语言
- **FastAPI 0.115.0**: 高性能 Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic 2.10.4**: 数据验证和设置管理
- **PyJWT**: JWT 令牌处理
- **HTTPX**: 异步 HTTP 客户端
- **Redis (可选)**: 持久化存储

### 前端
- **React 18**: UI 框架
- **TypeScript**: 类型安全
- **Vite 6**: 构建工具
- **React Router 6**: 路由管理
- **TailwindCSS**: 样式框架
- **Axios**: HTTP 客户端
- **Lucide React**: 图标库

### 外部服务
- **OpenCode 1.2.24**: 原生对话和技能引擎
- **OpenWork 0.11.142**: 文件管理

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 22+
- npm 10+
- OpenCode 1.2.24 (已安装)
- OpenWork 0.11.142 (已安装)

### 1. 安装后端依赖

```bash
cd backend
/home/yy/python312/bin/python -m pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量

创建 `backend/.env` 文件:

```bash
# 服务器配置
PORT=8000
HOST=0.0.0.0
RELOAD=true

# 存储配置 (使用内存存储，无需 Docker)
USE_REDIS=false
# 如果需要使用 Redis，设置 USE_REDIS=true 并启动 docker-compose
# REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OpenCode 配置
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENCODE_USERNAME=opencode
OPENCODE_PASSWORD=your-password

# OpenWork 配置
OPENWORK_BASE_URL=http://127.0.0.1:8787
OPENWORK_TOKEN=your-openwork-token

# Portal 配置
PORTAL_NAME=AI Portal
RESOURCES_PATH=config/resources.json
```

创建 `frontend/.env` 文件:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Portal
```

### 4. 启动 OpenCode 和 OpenWork 服务

```bash
# 启动 OpenCode 服务器
opencode serve --port 4096 --cors-origin=http://localhost:8000 --server-password=your-password

# 启动 OpenWork 服务器 (新终端)
openwork serve --workspace /path/to/workspace --daemon-port 8787
```

### 5. 启动 AI Portal 后端

```bash
cd backend
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 启动 AI Portal 前端

```bash
cd frontend
npm run dev
```

### 7. 访问应用

打开浏览器访问: `http://localhost:5173`

首次访问会自动跳转到模拟登录页面，使用默认员工号 `E10001` 登录。

## 开发指南

### 项目结构

```
agenthub/
├── backend/                    # 后端应用
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── models.py          # Pydantic 模型
│   │   ├── auth/              # 认证模块
│   │   │   ├── deps.py        # 认证依赖
│   │   │   ├── routes.py      # 认证路由
│   │   │   └── service.py     # SSO 服务
│   │   ├── catalog/           # 资源目录
│   │   │   └── service.py     # 目录服务
│   │   ├── acl/               # 访问控制
│   │   │   └── service.py     # ACL 服务
│   │   ├── adapters/          # 执行适配器
│   │   │   ├── base.py        # 基础适配器协议
│   │   │   ├── opencode.py    # 原生对话适配器
│   │   │   ├── skill_chat.py  # 技能对话适配器
│   │   │   ├── websdk.py      # WebSDK 适配器
│   │   │   └── openwork.py    # 文件管理适配器
│   │   ├── store/             # 数据存储
│   │   │   ├── memory_store.py  # 内存存储 (默认)
│   │   │   └── redis_store.py   # Redis 存储 (可选)
│   │   └── logging/           # 日志模块
│   │       └── middleware.py  # 追踪中间件
│   ├── config/
│   │   └── resources.json     # 资源目录配置
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── main.tsx           # 应用入口
│   │   ├── App.tsx            # 主应用组件
│   │   ├── types.ts           # TypeScript 类型定义
│   │   ├── api.ts             # API 客户端
│   │   ├── components/
│   │   │   ├── ResourceCard.tsx      # 资源卡片
│   │   │   ├── ChatInterface.tsx     # 聊天界面
│   │   │   ├── SessionSidebar.tsx    # 会话侧边栏
│   │   │   └── WorkspacePane.tsx     # 工作区面板
│   │   └── styles/
│   │       └── globals.css    # 全局样式
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── public/
│   └── sdk-host.html          # WebSDK iframe 宿主
├── docker-compose.yml         # Redis 服务 (可选)
└── README.md                  # 本文件
```

### 添加新资源

在 `backend/config/resources.json` 中添加新资源:

```json
{
  "id": "my-new-resource",
  "name": "我的新资源",
  "type": "skill_chat",
  "launch_mode": "native",
  "group": "技能助手",
  "description": "资源描述",
  "enabled": true,
  "tags": ["tag1", "tag2"],
  "config": {
    "skill_name": "my_skill",
    "starter_prompts": ["提示词1", "提示词2"],
    "workspace_id": "default"
  }
}
```

### 创建自定义适配器

1. 在 `backend/app/adapters/` 创建新文件
2. 继承 `ExecutionAdapter` 基类
3. 实现所有必需方法
4. 在 `backend/app/main.py` 中注册

```python
from .adapters.base import ExecutionAdapter

class MyAdapter(ExecutionAdapter):
    async def create_session(self, resource_id, user_context, config):
        # 实现会话创建
        pass

    async def send_message(self, session_id, message, trace_id=None):
        # 实现消息发送
        pass

    async def get_messages(self, session_id, trace_id=None):
        # 实现消息获取
        pass

    async def close_session(self, session_id, trace_id=None):
        # 实现会话关闭
        pass
```

## API 文档

### 认证 API

#### 模拟登录
```http
GET /api/auth/mock-login?emp_no=E10001
```

#### 获取当前用户
```http
GET /api/auth/me
```

#### 退出登录
```http
POST /api/auth/logout
```

### 资源 API

#### 列出所有资源
```http
GET /api/resources
```

#### 获取资源详情
```http
GET /api/resources/{resource_id}
```

#### 启动资源
```http
POST /api/resources/{resource_id}/launch
```

响应:
```json
{
  "kind": "native",
  "portal_session_id": "uuid"
}
```

或:
```json
{
  "kind": "websdk",
  "launch_id": "uuid"
}
```

### 会话 API

#### 列出用户会话
```http
GET /api/sessions?limit=50
```

#### 获取会话消息
```http
GET /api/sessions/{portal_session_id}/messages
```

#### 发送消息
```http
POST /api/sessions/{portal_session_id}/messages
Content-Type: application/json

{
  "text": "你好"
}
```

### WebSDK API

#### 获取嵌入配置
```http
GET /api/launches/{launch_id}/embed-config
```

### 技能 API

#### 列出所有技能
```http
GET /api/skills
```

## 配置说明

### 存储模式选择

系统支持两种存储模式:

#### 1. 内存存储 (默认，无需 Docker)
```bash
# .env
USE_REDIS=false
```

优点:
- 无需额外依赖
- 快速启动
- 适合开发和测试

缺点:
- 服务重启后数据丢失
- 不支持分布式部署

#### 2. Redis 存储 (可选)
```bash
# .env
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
```

启动 Redis:
```bash
docker-compose up -d
```

优点:
- 数据持久化
- 支持分布式部署

### OpenCode 配置

确保 OpenCode 服务器配置了 CORS 和认证:

```bash
opencode serve \
  --port 4096 \
  --cors-origin=http://localhost:8000 \
  --server-password=your-password
```

### OpenWork 配置

OpenWork 需要配置工作区和守护端口:

```bash
openwork serve \
  --workspace /path/to/workspace \
  --daemon-port 8787
```

## 部署指南

### 生产环境配置

1. **设置环境变量**
   ```bash
   export JWT_SECRET=your-production-secret
   export OPENCODE_BASE_URL=https://your-opencode-server
   export OPENWORK_BASE_URL=https://your-openwork-server
   export USE_REDIS=true
   export REDIS_URL=redis://your-redis-server:6379/0
   ```

2. **使用 Redis 存储**
   ```bash
   docker-compose up -d
   ```

3. **使用进程管理器**
   ```bash
   # 使用 gunicorn (推荐)
   cd backend
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

4. **构建前端**
   ```bash
   cd frontend
   npm run build
   ```

5. **使用 Nginx 服务静态文件**
   ```nginx
   server {
       listen 80;
       server_name your-portal.com;

       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 健康检查

```bash
curl http://localhost:8000/api/health
```

响应:
```json
{
  "status": "healthy",
  "portal_name": "AI Portal",
  "version": "1.0.0"
}
```

## 日志和调试

### 日志格式

系统使用 JSON 格式日志，包含追踪 ID:

```json
{
  "timestamp": "2026-03-26T10:00:00",
  "level": "INFO",
  "logger": "app.main",
  "message": "Request completed",
  "trace_id": "uuid",
  "emp_no": "E10001",
  "resource_id": "general-chat",
  "portal_session_id": "uuid",
  "engine_session_id": "uuid",
  "adapter": "opencode",
  "path": "/api/sessions/xxx/messages",
  "method": "POST",
  "status": 200,
  "cost_ms": 1234
}
```

### 查看日志

```bash
# 查看所有日志
tail -f logs/portal.log

# 过滤特定 trace_id
tail -f logs/portal.log | grep "trace_id"

# 使用 jq 解析 JSON
tail -f logs/portal.log | jq '.'
```

### 调试模式

在 `.env` 中设置:
```bash
RELOAD=true
LOG_LEVEL=DEBUG
```

## 常见问题

### Q: 如何更换存储模式?

A: 修改 `.env` 文件中的 `USE_REDIS` 变量:
- `USE_REDIS=false` - 使用内存存储
- `USE_REDIS=true` - 使用 Redis 存储

### Q: WebSDK 应用无法加载?

A: 检查:
1. OpenCode 服务器是否正在运行
2. CORS 配置是否正确
3. app_key 和 base_url 是否正确
4. 浏览器控制台是否有错误

### Q: 会话历史丢失?

A: 默认使用内存存储，服务重启后会丢失。如需持久化，设置 `USE_REDIS=true` 并启动 Redis。

### Q: 如何添加真实 SSO?

A: 在 `backend/app/auth/service.py` 中实现 `resolve_sso_user` 方法:
```python
async def resolve_sso_user(self, code: str) -> Optional[UserCtx]:
    # 调用真实 SSO API
    response = await self.sso_client.exchange_code_for_user(code)
    return UserCtx(**response)
```

### Q: 前端开发时出现 CORS 错误?

A: 检查 `backend/app/config.py` 中的 `cors_origins` 配置是否包含前端地址。

## 性能优化建议

1. **使用 Redis**: 生产环境推荐使用 Redis 存储
2. **缓存资源目录**: 资源列表变化不频繁，可以缓存
3. **连接池**: HTTPX 使用连接池提高性能
4. **前端优化**:
   - 启用代码分割
   - 使用 CDN 静态资源
   - 配置缓存策略

## 安全建议

1. **更改 JWT 密钥**: 生产环境使用强密钥
2. **启用 HTTPS**: 生产环境必须使用 HTTPS
3. **配置 CORS**: 仅允许可信域名
4. **输入验证**: 所有用户输入都经过 Pydantic 验证
5. **日志脱敏**: 避免在日志中记录敏感信息

## 许可证

本项目仅供企业内部使用。

## 联系方式

如有问题或建议，请联系开发团队。
