# AI Portal（统一入口）

AI Portal 是一个面向企业内部场景的统一 AI 入口，目标是把多种能力（原生聊天、Skill 聊天、知识库/旧应用 WebSDK、文件型 skill/config 管理）在一个门户中打通。

当前仓库实现遵循 V1 范围：
- **前台**：统一资源入口 + 聊天/嵌入式工作区。
- **中台**：Mock 鉴权、资源目录、ACL、会话中心、启动记录、Trace 日志。
- **执行层**：
  - `OpenCodeAdapter`（原生聊天）
  - `SkillChatAdapter`（Skill 对话）
  - `WebSDKAdapter`（知识库/旧应用嵌入）
  - `OpenWorkAdapter`（技能安装状态、引擎 reload）

---

## 文档导航

- [QUICKSTART.md](QUICKSTART.md)：5 分钟启动与验证
- [API.md](API.md)：后端接口清单（与当前代码一致）
- [DEVELOPMENT.md](DEVELOPMENT.md)：本地开发与调试
- [IMPLEMENTATION.md](IMPLEMENTATION.md)：V1 设计边界、模块职责、关键流程
- [TEST_REPORT.md](TEST_REPORT.md)：测试与验收说明
- [TEST_RESULTS_2026-03-26.md](TEST_RESULTS_2026-03-26.md)：历史测试快照

---

## V1 功能边界

### 已实现
- 统一资源目录与分组展示
- Mock SSO 登录（JWT Cookie）
- 原生对话会话管理（创建会话、发消息、拉历史）
- Skill 对话（系统提示注入 skill mode）
- WebSDK 资源启动记录（不托管其内部聊天历史）
- `sdk-host.html` 宿主页加载第三方 SDK
- Memory/Redis 双存储抽象
- Trace 中间件 + JSON 结构化日志

### 明确不做（V1）
- Skill 在线编辑器
- WebSDK 应用在 Portal 侧的会话回溯
- 知识库后台管理
- 多 Skill 编排

---

## 架构概览

```text
[Mock SSO / Future Real SSO]
          │
          ▼
      [Portal Web UI]
          │
          ▼
     [FastAPI BFF]
   ├─ Auth / ACL / Catalog
   ├─ Session Center (native+skill)
   ├─ Launch Record Center (websdk)
   ├─ OpenCodeAdapter
   ├─ SkillChatAdapter
   ├─ WebSDKAdapter
   └─ OpenWorkAdapter
          │
   ┌──────┼───────────────┐
   ▼      ▼               ▼
OpenCode  OpenWork        WebSDK Apps
```

---

## 快速启动

```bash
./scripts/start.sh
```

启动后访问：
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`
- OpenAPI：`http://localhost:8000/docs`

首次访问会触发 mock 登录流程（默认工号 `E10001`）。

> 详细步骤见 [QUICKSTART.md](QUICKSTART.md)。

---

## 核心实现约定

1. **Native/Skill 资源**：创建 `PortalSession`，并映射 OpenCode `session_id`。
2. **WebSDK 资源**：只创建 `LaunchRecord`，通过 `/api/launches/{launch_id}/embed-config` 提供嵌入配置。
3. **Skill 模式**：由 `SkillChatAdapter` 在发送消息时注入 system prompt，不依赖前端特殊逻辑。
4. **前端路由参数**：`/chat/:sessionId`、`/launch/:launchId` 使用 path param（`useParams`）读取。

---



## WebSDK 宿主页安全配置

为避免 `postMessage(..., '*')` 与任意脚本域名带来的风险，`public/sdk-host.html` 增加了来源与脚本域名白名单校验：

- **消息来源白名单**：仅当 `event.origin` 在 `allowedMessageOrigins` 中，才处理 `type: "init"`。
- **脚本 URL 校验**：
  - 默认要求 `https:`；
  - 开发环境允许 `http://localhost` / `http://127.0.0.1`；
  - `scriptUrl` 的主机名必须在 `allowedScriptHosts` 白名单内。
- **ready 消息**：宿主页对父页面发送 `{ type: "ready" }` 时使用明确 `targetOrigin`，不再使用 `*`。

可通过在宿主页提前注入全局配置覆盖默认值：

```html
<script>
  window.SDK_HOST_SECURITY = {
    allowedMessageOrigins: [
      'https://portal.example.com'
    ],
    allowedScriptHosts: [
      'sdk.example.com'
    ]
  };
</script>
```

> 建议在生产环境只保留实际 Portal 域名与 SDK 域名，避免后续接入时退化回 `*` 或宽松规则。

## 仓库结构（核心）

```text
backend/app/
├── main.py                # API 入口
├── adapters/              # 执行层适配器
├── auth/                  # mock 登录与用户依赖
├── catalog/               # 资源目录加载
├── acl/                   # 访问控制
├── store/                 # memory / redis 存储
└── logging/               # trace middleware

frontend/src/
├── App.tsx                # 路由与门户主页
├── api.ts                 # axios API 封装
├── types.ts               # 前端类型定义
└── components/            # 聊天、侧栏、工作区组件

public/
└── sdk-host.html          # WebSDK 宿主页
```
