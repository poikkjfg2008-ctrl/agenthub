# API 参考（当前实现）

Base URL: `http://localhost:8000`

认证方式：`access_token`（HTTP-only Cookie）

---

## 1. 系统

### `GET /api/health`
健康检查。

响应示例：
```json
{
  "status": "healthy",
  "portal_name": "AI Portal",
  "version": "1.0.0"
}
```

---

## 2. 认证

### `GET /api/auth/mock-login?emp_no=E10001`
Mock 登录，设置 Cookie。

响应示例：
```json
{
  "message": "Login successful",
  "redirect": "/",
  "user": {
    "emp_no": "E10001",
    "name": "User-E10001",
    "dept": "demo"
  }
}
```

### `GET /api/auth/me`
返回当前登录用户信息。

### `POST /api/auth/logout`
清除登录 Cookie。

---

## 3. 资源

### `GET /api/resources`
返回当前用户可访问资源（ACL 过滤后）。

### `GET /api/resources/grouped`
按 `group` 分组返回资源。

### `GET /api/resources/{resource_id}`
返回单个资源详情。

### `POST /api/resources/{resource_id}/launch`
启动资源。

- native 资源响应：
```json
{
  "kind": "native",
  "portal_session_id": "uuid"
}
```

- websdk 资源响应：
```json
{
  "kind": "websdk",
  "launch_id": "uuid"
}
```

---

## 4. 会话（native/skill）

### `GET /api/sessions?limit=50&resource_id=&type=&status=`
获取当前用户会话列表。支持按 `resource_id`、`type`（资源类型）、`status`（active/archived）过滤。

响应示例：
```json
{
  "sessions": [
    {
      "portal_session_id": "uuid",
      "resource_id": "general-chat",
      "resource_type": "direct_chat",
      "resource_name": "通用助手",
      "user_emp_no": "E10001",
      "title": "通用助手",
      "status": "active",
      "resource_snapshot": { "resource_id": "general-chat", "resource_name": "通用助手", ... },
      "created_at": "2026-03-26T12:00:00",
      "updated_at": "2026-03-26T12:05:00",
      "last_message_at": "2026-03-26T12:05:00",
      "last_message_preview": "你好",
      "metadata": { "adapter": "opencode" }
    }
  ]
}
```

### `GET /api/sessions/{portal_session_id}/messages`
返回会话消息。优先读取 Portal 本地持久化的 `PortalMessage`；若本地为空（如迁移场景），则回源 OpenCode 引擎并自动回填到本地存储。

```json
[
  {
    "role": "user",
    "text": "你好",
    "timestamp": "2026-03-26T12:00:00"
  }
]
```

### `POST /api/sessions/{portal_session_id}/messages`
发送消息（非流式）。后端会：
1. 保存 user `PortalMessage`
2. 通过 `SessionBinding` 调用对应 adapter
3. 保存 assistant `PortalMessage`
4. 更新会话 `last_message_preview` 和 `updated_at`

请求体：
```json
{ "text": "你好" }
```

响应体：
```json
{ "response": "...assistant text..." }
```

### `POST /api/sessions/{portal_session_id}/messages/stream`
发送消息（SSE 流式）。流结束后会将完整 assistant 内容持久化为 `PortalMessage`。

### `POST /api/sessions/{portal_session_id}/archive`
归档会话。

响应体：
```json
{ "success": true, "status": "archived" }
```

### `GET /api/sessions/{portal_session_id}/context`
获取该会话的合并上下文（global + user + user_resource + session）。

响应体：
```json
{
  "portal_session_id": "uuid",
  "scopes": {
    "global": {},
    "user": {},
    "user_resource": {},
    "session": {}
  },
  "merged": {}
}
```

---

## 5. WebSDK 启动记录

### `GET /api/launches?limit=50`
获取当前用户最近 WebSDK 启动记录。

### `GET /api/launches/{launch_id}/embed-config`
获取嵌入配置：
```json
{
  "script_url": "http://host/resources/.../embedLite.js",
  "app_key": "xxx",
  "base_url": "http://host/agent/chat",
  "launch_token": "token",
  "user_context": {
    "emp_no": "E10001"
  }
}
```

---

## 6. Skill 商店

### `GET /api/skills`
返回 Skill 资源与安装状态。

字段包含：
- `id/name/description`
- `skill_name`
- `starter_prompts`
- `installed`

## 7. 上下文管理

### `PATCH /api/contexts/user-resource/{resource_id}`
更新当前用户在指定资源下的上下文。

请求体：
```json
{
  "payload": { "preference": "dark_mode" },
  "summary": "用户偏好深色模式"
}
```

响应体：
```json
{ "success": true, "context_id": "uuid" }
```

## 8. 管理接口

### `POST /api/admin/resources/sync?workspace_id=default`
触发从 OpenWork 同步技能并重新生成 `resources.generated.json`。

响应体：
```json
{ "success": true, "count": 8, "workspace_id": "default" }
```

---

## 9. OpenAPI

交互式文档：`/docs`
