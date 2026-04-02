<!-- From: /home/yy/agenthub/AGENTS.md -->
<!-- This file provides essential information for AI coding agents working on the AI Portal project. -->

# AGENTS.md - AI Portal Project Guide

## Project Overview

**AI Portal（统一入口）** 是一个面向企业内部场景的统一 AI 门户，将多种 AI 能力整合到单一入口：

- **原生对话** (`direct_chat`): 通过 OpenCode API 直接与 AI 模型对话
- **技能对话** (`skill_chat`): 带有 specialized system prompt 的 AI 对话（编程、写作、数据分析等）
- **知识库** (`kb_websdk`): 通过 WebSDK 嵌入知识库应用
- **智能体应用** (`agent_websdk`): 通过 WebSDK 嵌入 AI Agent 应用
- **Iframe 集成** (`iframe`): 直接通过 iframe 嵌入第三方应用

**Architecture**: FastAPI 后端（BFF 模式）+ React（Vite）前端

```
[Mock SSO / Future Real SSO]
          │
          ▼
      [Portal Web UI] (React + Vite, port 5173)
          │
          ▼
     [FastAPI BFF] (Python 3.12+, port 8000)
   ├─ Auth / ACL / Catalog
   ├─ Session Center (native+skill)
   ├─ Launch Record Center (websdk+iframe)
   ├─ OpenCodeAdapter
   ├─ SkillChatAdapter
   ├─ WebSDKAdapter
   ├─ IframeAdapter
   └─ OpenWorkAdapter
          │
   ┌──────┼───────────────┐
   ▼      ▼               ▼
OpenCode  OpenWork        WebSDK/Iframe Apps
```

---

## Technology Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI 0.115+
- **Server**: Uvicorn 0.32+ (ASGI)
- **Configuration**: Pydantic Settings (`pydantic-settings>=2.2.1`)，从 `backend/.env` 加载
- **Storage**: In-memory（开发默认）/ Redis 7（生产），通过 `USE_REDIS` 切换
- **Authentication**: JWT Cookie-based，带 mock SSO fallback
- **HTTP Client**: httpx (AsyncClient)

**Key Dependencies** (from `backend/pyproject.toml`):
```toml
[project]
name = "ai-portal"
version = "1.0.0"
description = "AI Portal - Unified entry point for enterprise AI resources"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "redis>=5.2.0",
    "httpx>=0.28.1",
    "pyjwt>=2.10.1",
    "pydantic>=2.10.4",
    "pydantic-settings>=2.2.1",
    "python-multipart>=0.0.20",
]
```

### Frontend
- **Language**: TypeScript 5.7+
- **Framework**: React 18
- **Build Tool**: Vite 6.0+
- **Routing**: React Router DOM 6.28+
- **Styling**: Tailwind CSS 3.4+
- **HTTP Client**: Axios 1.7+
- **Icons**: Lucide React 0.468+
- **Markdown Rendering**:
  - `react-markdown` - Markdown 渲染
  - `remark-gfm` - GitHub Flavored Markdown
  - `remark-math` - 数学公式支持
  - `rehype-katex` - KaTeX 数学渲染
  - `rehype-highlight` - 代码语法高亮

### Infrastructure
- **Storage**: Memory（开发默认）/ Redis 7（生产），通过 `USE_REDIS` 环境变量切换
- **Container**: Docker Compose 仅用于 Redis 服务（`docker-compose.yml`）
- **Authentication**: JWT Cookie-based，带 mock SSO fallback

---

## Project Structure

```
agenthub/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口，定义全部路由
│   │   ├── config.py               # Pydantic Settings，从 .env 加载
│   │   ├── models.py               # 全部 Pydantic 模型
│   │   ├── adapters/
│   │   │   ├── base.py             # ExecutionAdapter 抽象基类
│   │   │   ├── opencode.py         # OpenCode API 适配器（原生对话）
│   │   │   ├── skill_chat.py       # Skill 模式适配器（system prompt 注入）
│   │   │   ├── websdk.py           # WebSDK 启动适配器
│   │   │   ├── iframe.py           # Iframe 嵌入适配器
│   │   │   └── openwork.py         # OpenWork API 适配器（技能管理）
│   │   ├── auth/
│   │   │   ├── service.py          # JWT 生成/验证 + mock 用户创建
│   │   │   ├── deps.py             # FastAPI 依赖（CurrentUser / OptionalUser）
│   │   │   └── routes.py           # 认证路由（/api/auth/*）
│   │   ├── catalog/
│   │   │   └── service.py          # 从 JSON 加载资源目录
│   │   ├── acl/
│   │   │   └── service.py          # 访问控制（资源过滤）
│   │   ├── store/
│   │   │   ├── __init__.py         # 存储选择器（Redis/Memory）
│   │   │   ├── memory_store.py     # 内存存储（OrderedDict + LRU）
│   │   │   └── redis_store.py      # Redis 持久化（async redis）
│   │   └── logging/
│   │       └── middleware.py       # Trace ID 中间件 + JSON 结构化日志
│   ├── config/
│   │   ├── resources.static.json   # 手工配置资源（direct_chat / websdk / iframe）
│   │   ├── resources.overrides.json # skill 产品层覆盖配置
│   │   └── resources.generated.json # 同步脚本产物（CatalogService 默认读取）
│   ├── tests/
│   │   ├── test_api.py             # 完整 API 测试
│   │   ├── test_api_simple.py      # 快速冒烟测试（推荐开发使用）
│   │   ├── test_preflight_check.py # preflight_check 单元测试
│   │   └── run_backend_tests.sh    # 后端测试运行脚本
│   ├── pyproject.toml              # Python 项目配置
│   ├── requirements.txt            # Python 依赖
│   └── .env                        # 后端环境变量（gitignored）
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # 主应用 + 路由（V2 三栏布局）
│   │   ├── api.ts                  # API 客户端（axios + SSE fetch）
│   │   ├── types.ts                # TypeScript 类型定义
│   │   ├── main.tsx                # 前端入口
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx   # 原生/skill 聊天 UI（支持 Markdown + 流式）
│   │   │   ├── SessionSidebar.tsx  # 会话列表面板
│   │   │   ├── ResourceSidebar.tsx # 资源侧边栏（分组可折叠）
│   │   │   ├── ResourceCard.tsx    # 资源卡片组件
│   │   │   ├── WorkspacePane.tsx   # WebSDK 工作区容器
│   │   │   └── IframeWorkspace.tsx # Iframe 嵌入组件
│   │   └── styles/
│   │       └── globals.css         # 全局样式 + Tailwind + Markdown 样式
│   ├── public/                     # 静态资源
│   ├── index.html                  # HTML 模板
│   ├── package.json                # NPM 配置
│   ├── tsconfig.json               # TypeScript 配置
│   ├── tailwind.config.js          # Tailwind 配置
│   └── vite.config.ts              # Vite 配置（port 5173，API proxy）
├── public/
│   └── sdk-host.html               # WebSDK 宿主页（iframe 内加载第三方 SDK）
├── scripts/
│   ├── start.sh                    # 启动所有服务（带前置检查）
│   ├── stop.sh                     # 停止所有服务
│   ├── test.sh                     # 测试脚本
│   ├── sync_resources.py           # 技能发现与资源同步脚本
│   └── preflight_check.py          # 启动前置依赖检查
├── logs/                           # 服务日志（gitignored）
├── docker-compose.yml              # Redis 服务配置
└── docs/                           # 文档目录
```

---

## Build and Development Commands

### Quick Start（Recommended）

```bash
# 启动所有服务（后端 + 前端），并执行前置检查
./scripts/start.sh

# 停止所有服务
./scripts/stop.sh

# 仅执行前置检查
python3 scripts/preflight_check.py

# CI 模式（不检查网络连通性）
python scripts/preflight_check.py --no-network
```

### Backend Development

```bash
cd backend

# 安装依赖
/home/yy/python312/bin/python -m pip install -r requirements.txt

# 运行开发服务器（热重载）
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行生产服务器
/home/yy/python312/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器（port 5173）
npm run dev

# 构建生产包
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

### Docker Services

```bash
# 启动 Redis
docker-compose up -d redis

# 停止 Redis
docker-compose down
```

---

## Service URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **OpenAPI Docs**: http://localhost:8000/docs
- **Redis** (if enabled): redis://localhost:6379

---

## Environment Configuration

### Backend (`backend/.env`)

```bash
# 服务器
PORT=8000
HOST=0.0.0.0
RELOAD=true

# 存储
USE_REDIS=false                    # true 启用 Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
AUTH_MOCK_FALLBACK_ENABLED=false   # 仅开发环境：认证失败回退 mock 用户

# OpenCode API
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENCODE_USERNAME=opencode
OPENCODE_PASSWORD=your-password

# OpenWork API
OPENWORK_BASE_URL=http://127.0.0.1:8787
OPENWORK_TOKEN=your-token

# Portal
PORTAL_NAME=AI Portal
RESOURCES_PATH=config/resources.generated.json

# 日志
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Portal
```

---

## Code Style Guidelines

### Python (Backend)

- **Style**: PEP 8
- **Docstrings**: Google style
- **Type Hints**: 函数签名使用 typing 模块
- **Async**: I/O 操作优先使用 async/await
- **Imports**: 分组顺序为标准库、第三方库、本地模块
- **Naming**: 函数/变量使用 snake_case，类使用 PascalCase
- **注释**: 代码注释中英混合，用户可见文本以中文为主

Example:
```python
"""Module docstring."""

from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .models import Resource


class ResourceService:
    """Service for resource operations."""

    async def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID.

        Args:
            resource_id: The resource identifier.

        Returns:
            Resource if found, None otherwise.
        """
        pass
```

### TypeScript (Frontend)

- **Style**: ESLint recommended + React Hooks rules
- **Types**: 接口定义在 `types.ts`，避免使用 `any`
- **Components**: 函数组件 + Hooks
- **Naming**: 组件/类型使用 PascalCase，函数/变量使用 camelCase
- **Imports**: 分组顺序为 React、第三方库、本地模块

Example:
```typescript
// types.ts
export interface Resource {
  id: string;
  name: string;
  type: ResourceType;
}

// Component
import { useState, useEffect } from 'react';
import type { Resource } from './types';

interface ResourceCardProps {
  resource: Resource;
  onLaunch: (r: Resource) => void;
}

export function ResourceCard({ resource, onLaunch }: ResourceCardProps) {
  // Implementation
}
```

---

## Testing Instructions

### Backend Tests

Located in `backend/tests/`:
- `test_api.py`: 综合 API 测试
- `test_api_simple.py`: 快速冒烟测试（推荐开发使用）
- `test_preflight_check.py`: `preflight_check.py` 的单元测试

Run with:
```bash
cd backend
/home/yy/python312/bin/python tests/test_api_simple.py
```

### Test Coverage Areas

1. **Health Check**: `/api/health`
2. **Auth Flow**: mock-login → me → logout
3. **Resources**: list, grouped, get by ID, launch
4. **Sessions**: list, get messages, send message
5. **WebSDK**: launch, get embed-config
6. **Iframe**: launch, get iframe-config
7. **Skills**: list with installation status
8. **Authorization**: 401 for unauthenticated requests

### Manual Testing

```bash
# 健康检查
curl http://localhost:8000/api/health

# Mock 登录（保存 cookie）
curl "http://localhost:8000/api/auth/mock-login?emp_no=E10001" -c cookies.txt

# 获取当前用户
curl http://localhost:8000/api/auth/me -b cookies.txt

# 列出资源
curl http://localhost:8000/api/resources -b cookies.txt

# 启动 native 资源
curl -X POST http://localhost:8000/api/resources/general-chat/launch -b cookies.txt
```

---

## Security Considerations

### Authentication

- 使用 JWT token 存储在 HTTP-only cookie 中
- 开发环境提供 mock 登录 (`/api/auth/mock-login`)
- 生产环境应替换为真实 SSO
- `AUTH_MOCK_FALLBACK_ENABLED` 仅供开发回退使用

### Authorization (ACL)

- 当前策略："未配置则允许"（permissive）
- 生产环境建议改为默认拒绝或最小权限
- ACL 规则支持：`allowed_roles`、`allowed_depts`、`allowed_users`、`denied_users`

### WebSDK Security

- `launch_token` 当前为随机字符串（`secrets.token_urlsafe(32)`）
- **TODO**: 生产环境升级为 signed JWT 或 HMAC 验证

### Iframe Security

- Iframe URL 在 `resources.json` 中配置
- 请确保仅使用可信域名

### CORS

- 默认允许 localhost 来源
- 生产环境请在 `CORS_ORIGINS` 中配置实际域名

### Secrets

- 生产环境必须修改 `JWT_SECRET`（强随机字符串）
- `OPENCODE_PASSWORD` 和 `OPENWORK_TOKEN` 应安全保管
- `.env` 文件已加入 `.gitignore`，切勿提交到版本控制

---

## Key Design Patterns

### 1. Adapter Pattern

所有执行后端实现 `ExecutionAdapter` 抽象基类：

```python
class ExecutionAdapter(ABC):
    @abstractmethod
    async def create_session(self, resource_id, user_context, config) -> str:
        pass

    @abstractmethod
    async def send_message(self, session_id, message, trace_id) -> str:
        pass

    @abstractmethod
    async def send_message_stream(self, session_id, message, trace_id) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def get_messages(self, session_id, trace_id) -> List[Message]:
        pass

    @abstractmethod
    async def close_session(self, session_id, trace_id) -> bool:
        pass

    @abstractmethod
    async def upload_file(self, session_id, file, description) -> Dict[str, Any]:
        pass
```

Adapters:
- `OpenCodeAdapter`: 原生对话会话（HTTP API 调用 OpenCode）
- `SkillChatAdapter`: Skill 模式，在发消息时注入 system prompt
- `WebSDKAdapter`: WebSDK 启动记录（返回 embed config）
- `IframeAdapter`: 直接 iframe 嵌入配置
- `OpenWorkAdapter`: 技能管理（安装状态、引擎 reload）

### 2. Storage Abstraction

统一存储接口，双实现：
- `MemoryStore`: 内存 OrderedDict（开发默认）
- `RedisStore`: Redis 持久化（生产）

存储层现在支持四层数据：
- **Sessions**: `save_session`, `get_session`, `list_user_sessions`, `delete_session`
- **Launches**: `save_launch`, `get_launch`, `list_user_launches`
- **Bindings**: `save_binding`, `get_binding`, `get_bindings_by_session`, `delete_binding`
- **Messages**: `save_message`, `get_message`, `list_session_messages`, `delete_session_messages`
- **Contexts**: `save_context`, `get_context`, `get_contexts_by_scope`, `delete_context`

通过 `USE_REDIS` 环境变量切换。

### 3. Resource Launch Modes

所有资源启动都会创建 `PortalSession` + `SessionBinding`：

| Launch Mode | Creates | Binding Type | Use Case |
|------------|---------|--------------|----------|
| `native` | `PortalSession` + `SessionBinding(engine_type="opencode")` | OpenCode session ID | 原生聊天、Skill 聊天 |
| `websdk` | `PortalSession` + `LaunchRecord` + `SessionBinding(engine_type="websdk")` | Launch ID | WebSDK 嵌入 |
| `iframe` | `PortalSession` + `LaunchRecord` + `SessionBinding(engine_type="iframe")` | Launch ID | 直接 iframe 嵌入 |

`PortalSession` 现在保存 `resource_snapshot`（启动时的资源配置快照），保证老会话不受后续配置变更影响。

### 4. Frontend Routing

使用 `useParams()` 读取 path param：
- `/chat/:sessionId` - 原生/skill 聊天
- `/launch/:launchId` - WebSDK iframe
- `/iframe/:launchId` - 直接 iframe

### 5. Frontend Layout (V2)

三栏响应式布局：
```
┌──────────────┬──────────────────────────────┬───────────────┐
│  Resource    │   Session Sidebar (optional) │   Chat/       │
│  Sidebar     │   + Chat Interface           │   Workspace   │
│  (w-72)      │                              │   (optional)  │
│  288px       │     flex-1                   │   380-600px   │
└──────────────┴──────────────────────────────┴───────────────┘
```

- **默认资源**: 启动时自动加载 `general-chat`
- **资源切换**: 点击左侧侧边栏资源切换对话
- **工作区切换**: WebSDK/iframe 资源可通过右上角按钮显示/隐藏右侧工作区

---

## Resource Types

| Type | Launch Mode | Description |
|------|-------------|-------------|
| `direct_chat` | native | 通用 AI 对话 |
| `skill_chat` | native | 带系统提示词的专业对话 |
| `kb_websdk` | websdk | 知识库 WebSDK 嵌入 |
| `agent_websdk` | websdk | Agent 应用 WebSDK 嵌入 |
| `iframe` | iframe | 直接 iframe 嵌入 |

### Resource Configuration Example

```json
{
  "id": "skill-coding",
  "name": "编程助手",
  "type": "skill_chat",
  "launch_mode": "native",
  "group": "技能助手",
  "description": "编程开发、代码审查、调试优化等开发任务",
  "enabled": true,
  "tags": ["coding", "development"],
  "config": {
    "skill_name": "coding",
    "starter_prompts": ["请帮我审查这段代码", "帮我优化这个函数"],
    "workspace_id": "default"
  },
  "acl": {
    "allowed_roles": ["employee", "admin"],
    "allowed_depts": ["Engineering", "IT"]
  },
  "sync_meta": {
    "origin": "static",
    "origin_key": "skill-coding"
  }
}
```

技能发现支持四层流水线：
1. **Discovery**: `scripts/sync_resources.py` 调用 OpenWork 拉取 skill 列表
2. **Normalization**: 将 OpenWork skill 映射为 Portal `Resource`
3. **Override**: `resources.overrides.json` 覆盖名称、分组、ACL、starter prompts
4. **Publish**: 输出 `resources.generated.json`，`CatalogService` 默认读取

---

## API Endpoints

### Health
- `GET /api/health` - 健康检查

### Authentication
- `GET /api/auth/mock-login?emp_no={id}` - Mock 登录
- `GET /api/auth/me` - 获取当前用户
- `POST /api/auth/logout` - 登出

### Resources
- `GET /api/resources` - 列出全部资源
- `GET /api/resources/grouped` - 按分组列出资源
- `GET /api/resources/{id}` - 获取资源详情
- `POST /api/resources/{id}/launch` - 启动资源

### Sessions (Native/Skill/Embedded)
- `GET /api/sessions` - 列出用户会话（支持 `resource_id`, `type`, `status`, `limit` 过滤）
- `GET /api/sessions/{id}` - 获取会话详情（返回 enriched 数据含 `resource_name`）
- `GET /api/sessions/{id}/messages` - 获取会话消息（优先读 Portal 持久化消息，空则回源引擎并回填）
- `POST /api/sessions/{id}/messages` - 发送消息（非流式，持久化 user + assistant 消息）
- `POST /api/sessions/{id}/messages/stream` - 发送消息（SSE 流式，完成后持久化 assistant 消息）
- `POST /api/sessions/{id}/upload` - 上传文件到会话
- `POST /api/sessions/{id}/archive` - 归档会话
- `GET /api/sessions/{id}/context` - 获取会话合并上下文

### Launches (WebSDK/Iframe)
- `GET /api/launches` - 列出启动记录
- `GET /api/launches/{id}/embed-config` - 获取 WebSDK 配置
- `GET /api/launches/{id}/iframe-config` - 获取 iframe 配置

### Contexts
- `PATCH /api/contexts/user-resource/{resource_id}` - 更新用户-资源级上下文

### Admin
- `POST /api/admin/resources/sync?workspace_id=default` - 触发资源同步

### Skills
- `GET /api/skills` - 列出技能及其安装状态

### Static
- `GET /sdk-host.html` - WebSDK 宿主页
- `GET /{full_path:path}` - 前端 SPA 回退（未登录则重定向到 mock-login）

---

## Important Files to Know

### Critical Backend Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI 入口，所有路由 |
| `app/config.py` | 从环境变量加载配置 |
| `app/models.py` | 全部 Pydantic 模型 |
| `app/adapters/base.py` | Adapter 协议定义 |
| `app/adapters/opencode.py` | OpenCode HTTP 客户端与流式解析 |
| `app/store/memory_store.py` | 内存存储实现 |
| `app/store/redis_store.py` | Redis 存储实现 |
| `config/resources.generated.json` | 资源目录配置（默认读取） |
| `scripts/sync_resources.py` | 技能发现与资源同步脚本 |

### Critical Frontend Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | 路由与主布局（V2 三栏设计） |
| `src/api.ts` | 全部 API 调用（含 SSE fetch） |
| `src/types.ts` | TypeScript 接口定义 |
| `src/components/ResourceSidebar.tsx` | 资源侧边栏（分组可折叠） |
| `src/components/ChatInterface.tsx` | 聊天 UI（Markdown + 文件上传 + 流式） |
| `src/components/WorkspacePane.tsx` | WebSDK 工作区 |
| `src/components/IframeWorkspace.tsx` | Iframe 工作区 |
| `public/sdk-host.html` | WebSDK 宿主页 |

---

## Common Issues and Solutions

### Issue: OpenCode connection errors

**Solution**: 检查 `backend/.env` 中的 `OPENCODE_BASE_URL`、`OPENCODE_USERNAME`、`OPENCODE_PASSWORD`

### Issue: WebSDK blank page

**Solution**:
1. 检查 `/api/launches/{launch_id}/embed-config` 是否返回正确数据
2. 确认 `public/sdk-host.html` 加载无错误
3. 检查浏览器控制台是否有 CORS 或脚本加载错误

### Issue: Redis connection failed

**Solution**:
1. 启动 Redis: `docker-compose up -d redis`
2. 或设置 `USE_REDIS=false` 使用内存存储

### Issue: Frontend can't connect to backend

**Solution**:
1. 确认后端在 8000 端口运行
2. 检查 `frontend/.env` 中的 `VITE_API_BASE_URL`
3. 确认后端 CORS 配置正确

---

## Documentation References

- [README.md](README.md): 项目概览与仓库结构
- [QUICKSTART.md](QUICKSTART.md): 5 分钟启动指南
- [API.md](API.md): 完整 API 参考
- [DEVELOPMENT.md](DEVELOPMENT.md): 开发工作流
- [PRESTART_CONDITIONS.md](PRESTART_CONDITIONS.md): 启动前置条件详情
- [WEBSDK_EMBEDDING_GUIDE.md](WEBSDK_EMBEDDING_GUIDE.md): WebSDK 配置指南
- [IMPLEMENTATION.md](IMPLEMENTATION.md): V1 设计与架构边界
- [docs/README.md](docs/README.md): 新用户配置指南
- [docs/FRONTEND_UI_V2_DEVELOPMENT.md](docs/FRONTEND_UI_V2_DEVELOPMENT.md): 前端 V2 功能说明
- [docs/01_START_OPENCODE_OPENWORK.md](docs/01_START_OPENCODE_OPENWORK.md): 启动 OpenCode/OpenWork
- [docs/02_CONFIGURE_AI_PORTAL.md](docs/02_CONFIGURE_AI_PORTAL.md): AI Portal 配置
- [docs/03_ADD_WEBSDK_RESOURCES.md](docs/03_ADD_WEBSDK_RESOURCES.md): 添加 WebSDK 资源

---

## Language Note

本项目主要使用 **中文** 作为以下场景的语言：
- 用户可见的 UI 文本
- 资源名称与描述
- 大部分文档文件
- 代码注释（中英混合）

修改代码或文档时，请保持与现有语言使用的一致性。
