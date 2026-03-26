# WebSDK 资源配置指南

本文档介绍如何将 WebSDK 资源添加到 AI Portal 的 resources.json 配置中。

---

## 一、WebSDK 概述

WebSDK 资源用于嵌入第三方的 AI 应用，如知识库、智能应用等。与 Native 对话不同，WebSDK 资源：

- 通过 iframe 嵌入第三方 SDK
- 不托管在 AI Portal 内部
- 通过 `launch_token` 进行安全验证

---

## 二、资源配置文件

### 2.1 文件位置

```
backend/config/resources.json
```

### 2.2 WebSDK 资源类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `kb_websdk` | 知识库 | 制度知识库、技术文档库 |
| `agent_websdk` | 智能应用 | 报表生成器、智能客服 |

---

## 三、添加 WebSDK 资源

### 3.1 基础配置模板

```json
{
  "id": "资源唯一标识",
  "name": "显示名称",
  "type": "kb_websdk",
  "launch_mode": "websdk",
  "group": "分组名称",
  "description": "资源描述",
  "enabled": true,
  "tags": ["kb", "标签1", "标签2"],
  "config": {
    "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
    "app_key": "your_app_key",
    "base_url": "http://127.0.0.1:4096/kb/chat"
  }
}
```

### 3.2 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `id` | ✅ | 唯一标识，如 `kb-policy`、`agent-report` |
| `name` | ✅ | 显示名称，如"制度知识库" |
| `type` | ✅ | `kb_websdk` 或 `agent_websdk` |
| `launch_mode` | ✅ | 固定为 `websdk` |
| `group` | ✅ | 分组名称，如"知识库"、"智能应用" |
| `config.script_url` | ✅ | SDK 脚本地址 |
| `config.app_key` | ✅ | 应用唯一标识 |
| `config.base_url` | ✅ | 服务基础地址 |

---

## 四、配置示例

### 4.1 知识库示例

```json
{
  "id": "kb-policy",
  "name": "制度知识库",
  "type": "kb_websdk",
  "launch_mode": "websdk",
  "group": "知识库",
  "description": "公司制度与流程问答，快速查找企业政策和规范",
  "enabled": true,
  "tags": ["kb", "policy", "hr"],
  "config": {
    "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
    "app_key": "kb_policy_key",
    "base_url": "http://127.0.0.1:4096/kb/chat"
  }
}
```

### 4.2 技术文档库示例

```json
{
  "id": "kb-tech",
  "name": "技术文档库",
  "type": "kb_websdk",
  "launch_mode": "websdk",
  "group": "知识库",
  "description": "技术文档、API参考、开发指南等技术资料查询",
  "enabled": true,
  "tags": ["kb", "tech", "dev"],
  "config": {
    "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
    "app_key": "kb_tech_key",
    "base_url": "http://127.0.0.1:4096/kb/chat"
  }
}
```

### 4.3 智能应用示例

```json
{
  "id": "agent-report",
  "name": "报表生成器",
  "type": "agent_websdk",
  "launch_mode": "websdk",
  "group": "智能应用",
  "description": "自动化报表生成与数据分析应用",
  "enabled": true,
  "tags": ["agent", "report", "data"],
  "config": {
    "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
    "app_key": "agent_report_key",
    "base_url": "http://127.0.0.1:4096/agent/chat"
  }
}
```

---

## 五、完整 resources.json 示例

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
  },
  {
    "id": "skill-coding",
    "name": "编程助手",
    "type": "skill_chat",
    "launch_mode": "native",
    "group": "技能助手",
    "description": "编程开发、代码审查、调试优化",
    "enabled": true,
    "tags": ["coding", "dev"],
    "config": {
      "skill_name": "coding",
      "starter_prompts": ["请帮我审查这段代码", "帮我优化这个函数"],
      "workspace_id": "default"
    }
  },
  {
    "id": "kb-policy",
    "name": "制度知识库",
    "type": "kb_websdk",
    "launch_mode": "websdk",
    "group": "知识库",
    "description": "公司制度与流程问答",
    "enabled": true,
    "tags": ["kb", "policy"],
    "config": {
      "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
      "app_key": "kb_policy_key",
      "base_url": "http://127.0.0.1:4096/kb/chat"
    }
  },
  {
    "id": "agent-report",
    "name": "报表生成器",
    "type": "agent_websdk",
    "launch_mode": "websdk",
    "group": "智能应用",
    "description": "自动化报表生成",
    "enabled": true,
    "tags": ["agent", "report"],
    "config": {
      "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
      "app_key": "agent_report_key",
      "base_url": "http://127.0.0.1:4096/agent/chat"
    }
  }
]
```

---

## 六、配置参数获取

### 6.1 从 OpenCode 获取 SDK 信息

```bash
# 检查 SDK 脚本是否存在
curl -I http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js

# 查看 OpenCode 提供的端点
curl http://127.0.0.1:4096/api/endpoints
```

### 6.2 参数对应关系

| 参数 | 说明 | 获取位置 |
|------|------|----------|
| `script_url` | SDK 脚本地址 | OpenCode 静态资源路径 |
| `app_key` | 应用标识 | OpenCode 应用配置 |
| `base_url` | 服务地址 | OpenCode API 基础地址 |

---

## 七、验证配置

### 7.1 配置格式检查

```bash
cd /path/to/agenthub

# 使用 Python 验证 JSON 格式
python3 -c "import json; json.load(open('backend/config/resources.json')); print('✅ JSON 格式正确')"
```

### 7.2 前置检查

```bash
# 执行前置检查（包含 WebSDK 端点检查）
python3 scripts/preflight_check.py
```

**预期输出**:
```
🔍 启动前置检查（OpenCode/OpenWork/WebSDK）
...
3. ✅ kb-policy.script_url: http://127.0.0.1:4096/... (127.0.0.1:4096)
4. ✅ kb-policy.base_url: http://127.0.0.1:4096/kb/chat (127.0.0.1:4096)
...
✅ 前置检查通过。
```

### 7.3 API 测试

```bash
# 登录并获取 cookie
curl -c cookies.txt "http://localhost:8000/api/auth/mock-login?emp_no=E10001"

# 启动 WebSDK 资源
curl -b cookies.txt -X POST http://localhost:8000/api/resources/kb-policy/launch

# 预期返回: {"kind":"websdk","launch_id":"xxx"}
```

---

## 八、前端展示效果

### 8.1 资源卡片

WebSDK 资源在首页以卡片形式展示：

```
┌─────────────────────────────┐
│ 📚 制度知识库    [kb_websdk] │
│ 公司制度与流程问答           │
│ #kb #policy         [启动]  │
└─────────────────────────────┘
```

### 8.2 启动后效果

点击"启动"后：
1. 调用 `POST /api/resources/{id}/launch`
2. 创建 `LaunchRecord`，生成 `launch_token`
3. 导航到 `/launch/{launch_id}`
4. 加载 `WorkspacePane` 组件
5. 渲染 iframe 加载 `/sdk-host.html`
6. 通过 postMessage 传递配置
7. SDK 在 iframe 中初始化

---

## 九、故障排查

### 9.1 SDK 脚本加载失败

**现象**: iframe 显示"WebSDK 脚本加载失败"

**排查**:
```bash
# 检查脚本是否可访问
curl -I http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js

# 如果不存在，检查 OpenCode 配置
# 或使用其他可用的 SDK 地址
```

### 9.2 嵌入配置获取失败

**现象**: 白屏或显示"加载失败"

**排查**:
```bash
# 检查 embed-config API
curl -b cookies.txt http://localhost:8000/api/launches/{launch_id}/embed-config

# 预期返回包含 script_url, app_key, base_url 等字段
```

### 9.3 iframe 通信失败

**现象**: SDK 不加载，console 报错

**排查**:
1. 检查浏览器控制台是否有跨域错误
2. 确认 `sdk-host.html` 中的 postMessage 监听正常
3. 检查 `WorkspacePane` 是否正确发送 init 消息

---

## 十、高级配置

### 10.1 动态配置（通过环境变量）

```bash
# backend/.env
WEBSDK_SCRIPT_URL=http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js
WEBSDK_BASE_URL=http://127.0.0.1:4096
```

然后在 `resources.json` 中使用占位符（需要代码支持）。

### 10.2 多环境配置

开发环境 `resources.dev.json`:
```json
{
  "config": {
    "script_url": "http://localhost:4096/sdk.js",
    "base_url": "http://localhost:4096"
  }
}
```

生产环境 `resources.prod.json`:
```json
{
  "config": {
    "script_url": "https://cdn.example.com/sdk.js",
    "base_url": "https://api.example.com"
  }
}
```

通过环境变量切换:
```bash
RESOURCES_PATH=config/resources.prod.json
```

---

## 十一、安全建议

### 11.1 launch_token 安全

- `launch_token` 是随机生成的安全令牌
- 默认有效期与 session 相同
- 生产环境建议添加 JWT 签名验证

### 11.2 iframe 安全

```html
<!-- sdk-host.html 中的 sandbox 配置 -->
<iframe sandbox="allow-same-origin allow-scripts allow-forms allow-popups">
```

### 11.3 域名白名单

生产环境限制 postMessage 目标域名:

```javascript
// sdk-host.html
window.parent.postMessage({ type: 'ready' }, 'https://your-domain.com');
```

---

## 相关文档

- [01_START_OPENCODE_OPENWORK.md](./01_START_OPENCODE_OPENWORK.md) - OpenCode/OpenWork 启动指南
- [02_CONFIGURE_AI_PORTAL.md](./02_CONFIGURE_AI_PORTAL.md) - AI Portal 配置指南
- [WEBSDK_EMBEDDING_GUIDE.md](../WEBSDK_EMBEDDING_GUIDE.md) - WebSDK 嵌入详细指南
