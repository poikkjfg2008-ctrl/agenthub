# AI Portal 文档中心

本文档中心提供 AI Portal 的完整配置和使用指南。

---

## 📚 文档导航

| 文档 | 内容 | 阅读顺序 |
|------|------|----------|
| [01_START_OPENCODE_OPENWORK.md](./01_START_OPENCODE_OPENWORK.md) | 启动 OpenCode 和 OpenWork 服务 | 第1步 |
| [02_CONFIGURE_AI_PORTAL.md](./02_CONFIGURE_AI_PORTAL.md) | 配置 AI Portal 项目 | 第2步 |
| [03_ADD_WEBSDK_RESOURCES.md](./03_ADD_WEBSDK_RESOURCES.md) | 添加 WebSDK 资源 | 第3步（可选） |

---

## 🚀 快速开始

### 5 分钟启动指南

```bash
# 1. 启动 OpenCode（终端1）
cd /path/to/opencode
source venv/bin/activate
python -m opencode --port 4096

# 2. 启动 OpenWork（终端2）
cd /path/to/openwork
npm run dev

# 3. 启动 AI Portal（终端3）
cd /path/to/agenthub
./scripts/start.sh

# 4. 访问 http://localhost:5173
```

---

## 📖 详细文档

### 文档1: OpenCode 和 OpenWork 启动指南

**文件**: `01_START_OPENCODE_OPENWORK.md`

**内容包括**:
- OpenCode 安装和启动
- OpenWork 安装和启动
- systemd 服务配置
- Docker 启动方式
- 故障排查

**关键命令**:
```bash
# OpenCode
python -m opencode --port 4096

# OpenWork
npm run dev

# 验证
curl http://127.0.0.1:4096
curl http://127.0.0.1:8787
```

---

### 文档2: AI Portal 配置指南

**文件**: `02_CONFIGURE_AI_PORTAL.md`

**内容包括**:
- 配置文件位置
- 后端环境变量配置
- 前端环境变量配置
- 配置验证
- 生产环境配置

**关键配置**:
```bash
# backend/.env
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENWORK_BASE_URL=http://127.0.0.1:8787
RELOAD=false
USE_REDIS=false
```

---

### 文档3: WebSDK 资源配置指南

**文件**: `03_ADD_WEBSDK_RESOURCES.md`

**内容包括**:
- WebSDK 概述
- 资源类型说明
- 配置模板
- 配置示例
- 验证方法

**关键配置**:
```json
{
  "id": "kb-policy",
  "name": "制度知识库",
  "type": "kb_websdk",
  "launch_mode": "websdk",
  "group": "知识库",
  "config": {
    "script_url": "http://127.0.0.1:4096/sdk.js",
    "app_key": "kb_policy_key",
    "base_url": "http://127.0.0.1:4096/kb/chat"
  }
}
```

---

## 🔧 常用操作

### 配置检查

```bash
# 前置检查
python3 scripts/preflight_check.py

# JSON 格式检查
python3 -c "import json; json.load(open('backend/config/resources.json'))"
```

### 服务管理

```bash
# 启动
./scripts/start.sh

# 停止
./scripts/stop.sh

# 重启
./scripts/stop.sh && ./scripts/start.sh
```

### 日志查看

```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log
```

---

## 🌐 访问地址

服务启动后，可通过以下地址访问：

| 服务 | URL | 说明 |
|------|-----|------|
| AI Portal 前端 | http://localhost:5173 | 用户界面 |
| AI Portal 后端 | http://localhost:8000 | API 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| OpenCode | http://127.0.0.1:4096 | AI 引擎 |
| OpenWork | http://127.0.0.1:8787 | Skill 服务 |

---

## 📁 项目结构

```
agenthub/
├── docs/                           # 文档目录
│   ├── README.md                   # 本文档
│   ├── 01_START_OPENCODE_OPENWORK.md
│   ├── 02_CONFIGURE_AI_PORTAL.md
│   └── 03_ADD_WEBSDK_RESOURCES.md
├── backend/
│   ├── .env                        # 后端配置（从此文件创建）
│   ├── config/
│   │   └── resources.json          # 资源配置
│   └── app/
├── frontend/
│   └── .env                        # 前端配置（可选）
├── scripts/
│   ├── start.sh                    # 启动脚本
│   ├── stop.sh                     # 停止脚本
│   └── preflight_check.py          # 前置检查
└── public/
    └── sdk-host.html               # WebSDK 宿主页
```

---

## ⚠️ 常见问题

### 问题1: 前置检查失败

**解决**: [查看详细排查步骤](./01_START_OPENCODE_OPENWORK.md#五故障排查)

### 问题2: 配置不生效

**解决**: [查看配置加载说明](./02_CONFIGURE_AI_PORTAL.md#六启动-ai-portal)

### 问题3: WebSDK 加载失败

**解决**: [查看 WebSDK 故障排查](./03_ADD_WEBSDK_RESOURCES.md#九故障排查)

---

## 📞 获取更多帮助

- 查看项目根目录的 `README.md`
- 查看 `CLAUDE.md` 了解项目架构
- 查看 `WEBSDK_EMBEDDING_GUIDE.md` 了解 WebSDK 详情

---

**最后更新**: 2026-03-27
