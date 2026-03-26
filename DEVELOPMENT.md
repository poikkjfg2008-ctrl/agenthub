# Development Guide

## 1. 项目结构

```text
agenthub/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── adapters/
│   │   ├── auth/
│   │   ├── catalog/
│   │   ├── acl/
│   │   ├── store/
│   │   └── logging/
│   ├── config/resources.json
│   └── tests/
├── frontend/src/
│   ├── App.tsx
│   ├── api.ts
│   ├── types.ts
│   └── components/
├── public/sdk-host.html
└── scripts/
```

---

## 2. 本地开发

### 安装
```bash
cd backend && /home/yy/python312/bin/python -m pip install -r requirements.txt
cd ../frontend && npm install
```

### 运行
```bash
# 后端
cd backend
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm run dev
```

---

## 3. 配置项（关键）

后端读取 `backend/.env`（见 `app/config.py`）：
- `USE_REDIS` / `REDIS_URL`
- `OPENCODE_BASE_URL` / `OPENCODE_USERNAME` / `OPENCODE_PASSWORD`
- `OPENWORK_BASE_URL` / `OPENWORK_TOKEN`
- `RESOURCES_PATH`

资源目录默认文件：`backend/config/resources.json`。

---

## 4. 开发约定

1. **资源分流不变**：
   - `launch_mode=native` => `PortalSession`
   - `launch_mode=websdk` => `LaunchRecord`
2. **Skill 行为在后端适配器实现**：前端只按普通 session 发送消息。
3. **WebSDK 宿主页只做加载与初始化**：不要在主 React 应用中直接注入第三方 SDK 全局对象。
4. **trace 透传**：通过 `request.state.trace_context` 读取并向下游透传。

---

## 5. 测试

### 后端
```bash
cd backend
/home/yy/python312/bin/python tests/test_api_simple.py
/home/yy/python312/bin/python tests/test_api.py
```

### 前端
当前仓库提供 `frontend/index.test.html` 与 `frontend/src/tests/*` 作为手工/示例测试入口。

---

## 6. 常见改造点

- 接真实 SSO：替换 `auth/service.py` 中 mock 逻辑，保持 Cookie 协议不变。
- WebSDK 安全票据：将随机 `launch_token` 升级为可验签 JWT/HMAC。
- OpenWork 技能安装状态：可从“单 skill 查询”改为“list 后本地匹配”。


---

## 7. 补充文档

- 启动前置条件：`PRESTART_CONDITIONS.md`
- WebSDK 嵌入与配置：`WEBSDK_EMBEDDING_GUIDE.md`
