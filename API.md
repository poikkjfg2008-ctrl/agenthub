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

### `GET /api/sessions?limit=50`
获取当前用户会话列表。

响应示例：
```json
{
  "sessions": [
    {
      "portal_session_id": "uuid",
      "engine_session_id": "opencode_session_id",
      "resource_id": "general-chat",
      "user_emp_no": "E10001",
      "created_at": "2026-03-26T12:00:00",
      "updated_at": "2026-03-26T12:05:00",
      "metadata": {
        "adapter": "opencode"
      }
    }
  ]
}
```

### `GET /api/sessions/{portal_session_id}/messages`
返回标准化后的消息数组：
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
请求体：
```json
{ "text": "你好" }
```

响应体：
```json
{ "response": "...assistant text..." }
```

> 说明：当前后端会从 OpenCode 的 `{info, parts}` 结构中提取纯文本后返回。

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

---

## 7. OpenAPI

交互式文档：`/docs`
