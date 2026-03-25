# API 参考文档

完整的 API 端点参考文档。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **认证方式**: JWT Token (HTTP-only Cookie)

## 认证

### 模拟登录

模拟 SSO 登录，用于开发测试。

**端点**: `GET /api/auth/mock-login`

**参数**:
- `emp_no` (query): 员工号，例如: `E10001`

**响应**: 302 重定向到首页

**示例**:
```bash
curl "http://localhost:8000/api/auth/mock-login?emp_no=E10001" -c cookies.txt
```

### 获取当前用户

获取当前登录用户的信息。

**端点**: `GET /api/auth/me`

**响应**:
```json
{
  "emp_no": "E10001",
  "name": "User-E10001",
  "dept": "demo",
  "roles": ["employee"],
  "email": "E10001@company.com"
}
```

**示例**:
```bash
curl http://localhost:8000/api/auth/me -b cookies.txt
```

### 退出登录

清除用户认证信息。

**端点**: `POST /api/auth/logout`

**响应**:
```json
{
  "message": "Logged out successfully"
}
```

## 资源

### 列出所有资源

获取当前用户可访问的所有资源。

**端点**: `GET /api/resources`

**响应**:
```json
[
  {
    "id": "general-chat",
    "name": "通用助手",
    "type": "direct_chat",
    "launch_mode": "native",
    "group": "基础对话",
    "description": "通用问答与任务协助",
    "enabled": true,
    "tags": ["chat", "general"],
    "config": {
      "workspace_id": "default",
      "model": "default"
    }
  }
]
```

**资源类型**:
- `direct_chat`: 直接对话
- `skill_chat`: 技能对话
- `kb_websdk`: 知识库 (WebSDK)
- `agent_websdk`: Agent 应用 (WebSDK)

**启动模式**:
- `native`: 原生聊天界面
- `websdk`: iframe 嵌入

### 列出分组资源

获取按分组组织的资源。

**端点**: `GET /api/resources/grouped`

**响应**:
```json
{
  "基础对话": [...],
  "技能助手": [...],
  "知识库": [...]
}
```

### 获取资源详情

获取指定资源的详细信息。

**端点**: `GET /api/resources/{resource_id}`

**参数**:
- `resource_id` (path): 资源 ID

**响应**: 单个 Resource 对象

**示例**:
```bash
curl http://localhost:8000/api/resources/general-chat -b cookies.txt
```

### 启动资源

启动一个资源，创建会话或生成启动令牌。

**端点**: `POST /api/resources/{resource_id}/launch`

**参数**:
- `resource_id` (path): 资源 ID

**响应 (Native 模式)**:
```json
{
  "kind": "native",
  "portal_session_id": "uuid-v4"
}
```

**响应 (WebSDK 模式)**:
```json
{
  "kind": "websdk",
  "launch_id": "uuid-v4"
}
```

**示例**:
```bash
curl -X POST http://localhost:8000/api/resources/general-chat/launch -b cookies.txt
```

## 会话

### 列出用户会话

获取当前用户的会话列表。

**端点**: `GET /api/sessions`

**参数**:
- `limit` (query, optional): 返回数量限制，默认 50

**响应**:
```json
{
  "sessions": [
    {
      "portal_session_id": "uuid",
      "engine_session_id": "uuid",
      "resource_id": "general-chat",
      "user_emp_no": "E10001",
      "created_at": "2026-03-26T10:00:00",
      "updated_at": "2026-03-26T10:30:00",
      "metadata": {
        "adapter": "opencode"
      }
    }
  ]
}
```

### 获取会话消息

获取指定会话的消息历史。

**端点**: `GET /api/sessions/{portal_session_id}/messages`

**参数**:
- `portal_session_id` (path): Portal 会话 ID

**响应**:
```json
[
  {
    "role": "user",
    "text": "你好",
    "timestamp": "2026-03-26T10:00:00"
  },
  {
    "role": "assistant",
    "text": "你好！有什么我可以帮助你的吗？",
    "timestamp": "2026-03-26T10:00:01"
  }
]
```

**角色类型**:
- `user`: 用户消息
- `assistant`: 助手回复
- `system`: 系统消息

**示例**:
```bash
curl http://localhost:8000/api/sessions/{session_id}/messages -b cookies.txt
```

### 发送消息

向指定会话发送消息。

**端点**: `POST /api/sessions/{portal_session_id}/messages`

**请求体**:
```json
{
  "text": "你好，请介绍一下你自己"
}
```

**响应**:
```json
{
  "response": "我是AI助手，可以帮助你..."
}
```

**示例**:
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "你好"}' \
  -b cookies.txt
```

## WebSDK

### 获取嵌入配置

获取 WebSDK 应用的嵌入配置。

**端点**: `GET /api/launches/{launch_id}/embed-config`

**参数**:
- `launch_id` (path): 启动记录 ID

**响应**:
```json
{
  "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
  "app_key": "kb_policy_key",
  "base_url": "http://127.0.0.1:4096/kb/chat",
  "launch_token": "url-safe-token",
  "user_context": {
    "emp_no": "E10001",
    "name": "User-E10001",
    "dept": "demo",
    "email": "E10001@company.com"
  }
}
```

**示例**:
```bash
curl http://localhost:8000/api/launches/{launch_id}/embed-config -b cookies.txt
```

### 列出用户启动记录

获取当前用户的 WebSDK 应用启动记录。

**端点**: `GET /api/launches`

**参数**:
- `limit` (query, optional): 返回数量限制，默认 50

**响应**:
```json
{
  "launches": [
    {
      "launch_id": "uuid",
      "resource_id": "kb-policy",
      "user_emp_no": "E10001",
      "launched_at": "2026-03-26T10:00:00",
      "launch_token": "token",
      "user_context": {...}
    }
  ]
}
```

## 技能

### 列出所有技能

获取所有技能及其安装状态。

**端点**: `GET /api/skills`

**响应**:
```json
[
  {
    "id": "skill-coding",
    "name": "编程助手",
    "description": "编程开发、代码审查、调试优化等开发任务",
    "installed": true,
    "skill_name": "coding",
    "starter_prompts": [
      "请帮我审查这段代码",
      "帮我优化这个函数",
      "解释这段代码的作用"
    ]
  }
]
```

**示例**:
```bash
curl http://localhost:8000/api/skills -b cookies.txt
```

## 系统

### 健康检查

检查系统健康状态。

**端点**: `GET /api/health`

**响应**:
```json
{
  "status": "healthy",
  "portal_name": "AI Portal",
  "version": "1.0.0"
}
```

**示例**:
```bash
curl http://localhost:8000/api/health
```

## 错误响应

所有错误响应遵循统一格式:

```json
{
  "detail": "错误描述信息"
}
```

**HTTP 状态码**:
- `200`: 成功
- `400`: 请求错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源未找到
- `500`: 服务器错误

## 请求头

### 请求头

所有 API 请求自动包含以下请求头:

```
Content-Type: application/json
Cookie: access_token=<jwt_token>
```

### 响应头

所有 API 响应包含以下响应头:

```
X-Trace-ID: <trace_id>
Content-Type: application/json
```

## 速率限制

当前版本未实施速率限制。未来版本可能会添加:

- 每用户每分钟请求数限制
- 每个会话的消息发送频率限制
- 并发会话数量限制

## 版本控制

API 当前版本: `v1.0.0`

未来版本可能:
- 添加新端点
- 修改响应格式
- 添加新的请求参数

向后兼容性会在主要版本更新时保持。

## SDK 和客户端

### Python SDK

```python
from ai_portal import PortalClient

client = PortalClient(base_url="http://localhost:8000")

# 模拟登录
client.mock_login("E10001")

# 列出资源
resources = client.list_resources()

# 启动资源
launch = client.launch_resource("general-chat")

# 发送消息
response = client.send_message(launch.portal_session_id, "你好")
```

### JavaScript SDK

```typescript
import { PortalClient } from '@ai-portal/sdk';

const client = new PortalClient({
  baseURL: 'http://localhost:8000'
});

// 列出资源
const resources = await client.resources.list();

// 启动资源
const launch = await client.resources.launch('general-chat');

// 发送消息
const response = await client.sessions.sendMessage(
  launch.portal_session_id,
  '你好'
);
```

## WebHooks

当前版本未支持 WebHooks。未来版本可能会添加:

- 会话创建事件
- 消息发送事件
- 资源启动事件

## 限制和配额

### 会话限制

- 每用户最大并发会话数: 100
- 会话历史消息保留: 无限制 (内存模式受限)
- 会话超时: 无限制

### 消息限制

- 单条消息最大长度: 10000 字符
- 消息发送速率: 无限制

### 文件上传

当前版本不支持文件上传。未来版本可能会支持。

## 测试环境

### 本地开发

- Base URL: `http://localhost:8000`
- 模拟登录: `/api/auth/mock-login?emp_no=E10001`

### 测试环境

- Base URL: `https://test-portal.company.com`
- 真实 SSO: `/api/auth/callback`

### 生产环境

- Base URL: `https://portal.company.com`
- 真实 SSO: `/api/auth/callback`
