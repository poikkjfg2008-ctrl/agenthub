# Implementation Notes（V1）

本文档用于对齐“历史设计目标”与“当前代码实现”。

## 1. 目标与范围

### 目标
构建企业统一 AI 入口：
- 聊天 + 资源切换 WebUI
- 统一鉴权、资源目录、权限、会话、日志
- 多执行层（OpenCode / WebSDK / OpenWork）

### V1 范围
- ✅ 统一入口
- ✅ mock SSO
- ✅ 资源目录 + ACL
- ✅ 原生对话 / skill 对话
- ✅ WebSDK 入口统一 + 启动记录统一
- ✅ trace + JSON 日志

### V1 非目标
- ❌ Skill 在线编辑
- ❌ Portal 托管 WebSDK 历史回溯
- ❌ 复杂编排/审批流

---

## 2. 执行层设计

### OpenCodeAdapter
- `POST /session` 创建会话（title）
- `POST /session/{id}/message` 发消息（parts + optional system）
- `GET /session/{id}/message` 拉历史并标准化为 `Message(role,text,timestamp)`

### SkillChatAdapter
- 会话创建时记录 `session_id -> skill_name`
- 发消息时注入 skill mode 系统提示
- 其余行为委托 OpenCodeAdapter

### WebSDKAdapter
- 生成 `launch_token`
- 写入 `LaunchRecord`
- 返回 `script_url/app_key/base_url` 等 embed 配置

### OpenWorkAdapter
- 查询技能列表/状态
- 支持触发引擎 reload

---

## 3. 前后端协作关键点

1. **路由参数**
   - `/chat/:sessionId`
   - `/launch/:launchId`
   - 前端通过 `useParams` 获取 path params。

2. **WebSDK 宿主页**
   - 使用 `sdk-host.html`
   - 接收 config 后加载 `scriptUrl`
   - 调用 `new HiagentWebSDK.WebLiteClient({...})`

3. **会话更新时间**
   - 每次 `POST /api/sessions/{id}/messages` 后更新 `session.updated_at`

---

## 4. 存储模型

- `PortalSession`：native/skill 会话中心
- `LaunchRecord`：websdk 启动记录中心
- 存储实现：
  - `MemoryStore`（默认开发态）
  - `RedisStore`（可选生产态）

---

## 5. 风险与后续改进

1. `mock-login` 返回 JSON 与“重定向式登录”存在行为差异，可后续统一。
2. `launch_token` 当前为随机串，建议升级到签名票据（JWT/HMAC）。
3. ACL 现为“未配置即放行”，企业场景建议转向默认拒绝或最小权限。
4. OpenWork 的 skill detail endpoint 兼容性需根据目标版本进一步确认。
