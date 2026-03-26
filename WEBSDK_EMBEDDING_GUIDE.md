# WebSDK 嵌入与 Adapter 配置指南（智能应用 + 知识库）

## 1. 目标

本文说明如何把你已有的 WebSDK，接入本仓库中的两类资源：
- 知识库应用（`type=kb_websdk`）
- 智能应用（`type=agent_websdk`）

并说明如何按实际环境调整：
- 资源配置（`resources.json`）
- 后端 adapter 行为
- 宿主页与前端路由参数

---

## 2. 最小可用配置（resources.json）

每个 WebSDK 资源至少需要：
- `script_url`: SDK JS 地址
- `app_key`: 应用标识
- `base_url`: SDK 业务接口基础地址

示例（知识库）：

```json
{
  "id": "kb-policy",
  "type": "kb_websdk",
  "launch_mode": "websdk",
  "config": {
    "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
    "app_key": "kb_policy_key",
    "base_url": "http://127.0.0.1:4096/kb/chat"
  }
}
```

示例（智能应用）：

```json
{
  "id": "agent-report",
  "type": "agent_websdk",
  "launch_mode": "websdk",
  "config": {
    "script_url": "http://127.0.0.1:4096/resources/product/llm/public/sdk/embedLite.js",
    "app_key": "agent_report_key",
    "base_url": "http://127.0.0.1:4096/agent/chat"
  }
}
```

---

## 3. 接入流程（推荐）

1. 在 `backend/config/resources.json` 新增或修改 `websdk` 资源。
2. 启动前执行 `scripts/preflight_check.py`，确认端点可达。
3. 通过 `/api/resources/{id}/launch` 启动资源，拿到 `launch_id`。
4. 前端访问 `/launch/{launch_id}`。
5. 前端调用 `/api/launches/{launch_id}/embed-config` 获取 SDK 初始化参数。
6. `public/sdk-host.html` 按返回参数加载脚本并初始化 SDK。

---

## 4. 如何按你的环境调整配置

### 4.1 开发 / 测试 / 生产地址切换

建议把 `script_url` 与 `base_url` 抽为环境差异配置（至少区分 dev/prod）。

可选策略：
- 直接维护多份 `resources.json`，通过 `RESOURCES_PATH` 切换。
- 保留单份资源文件，由部署流程替换域名。

### 4.2 app_key 管理

- 不同应用用不同 `app_key`。
- 建议与资源 ID 建立一一映射，便于排障。
- 如涉及租户，建议加租户前缀（例如：`tenantA_kb_policy`）。

### 4.3 鉴权票据

当前 Portal 会返回 `launch_token`。如果你的 SDK 需要更强校验：
- 将 token 升级为 JWT/HMAC（带过期时间、签名、资源 ID）。
- 在 WebSDK 服务端验证 token 与 `app_key`、`resource_id` 一致性。

---

## 5. Adapter 调整建议

> 如果你的 WebSDK 初始化参数与当前字段不同，优先改后端 Adapter 的输出结构，而不是让前端写大量 if/else 分支。

建议步骤：
1. 在 WebSDK Adapter 内维护“平台无关字段”到“供应商 SDK 字段”的映射层。
2. `/embed-config` 统一返回前端可消费结构。
3. `sdk-host.html` 只做渲染与调用，不内嵌业务规则。

常见改造点：
- 字段重命名（如 `app_key` -> `clientId`）。
- 初始化参数拆分（如 region / locale / theme）。
- 事件回调桥接（消息上报、错误上报、埋点透传）。

---

## 6. 前端与宿主页改造边界

### 建议保持
- React 主应用只负责：路由、launch 获取、容器挂载。
- `sdk-host.html` 负责：动态注入 SDK、初始化、异常兜底展示。

### 不建议
- 在 React 组件里直接依赖 SDK 全局对象并处理复杂生命周期。
- 将业务鉴权逻辑硬编码在前端。

---

## 7. 自检清单

- [ ] `resources.json` 中目标资源 `enabled=true`。
- [ ] `launch_mode=websdk`。
- [ ] `script_url`、`base_url` 可访问。
- [ ] `/api/resources/{id}/launch` 返回 `kind=websdk`。
- [ ] `/api/launches/{launch_id}/embed-config` 返回完整初始化配置。
- [ ] 页面无跨域/混合内容报错（http/https 协议一致）。

---

## 8. 示例：新增一个知识库应用

1. 新增资源项 `id=kb-hr`，配置 `script_url/app_key/base_url`。
2. 运行前置检查并启动服务。
3. 调用 `POST /api/resources/kb-hr/launch`。
4. 在前端打开 `/launch/{launch_id}` 验证 SDK 是否正常加载。

如果你的 SDK 初始化参数更多，先扩展后端返回结构，再在 `sdk-host.html` 做最小增量适配。
