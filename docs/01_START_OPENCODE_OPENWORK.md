# OpenCode 和 OpenWork 启动指南

本文档介绍如何启动 OpenCode 和 OpenWork 服务，作为 AI Portal 的依赖后端。

---

## 一、OpenCode 启动

### 1.1 环境要求

- Python 3.10+
- 推荐使用虚拟环境

### 1.2 安装步骤

```bash
# 进入 OpenCode 目录（根据实际路径调整）
cd /path/to/opencode

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 1.3 启动服务

```bash
# 方式1: 默认启动（端口 4096）
python -m opencode

# 方式2: 指定端口
python -m opencode --port 4096

# 方式3: 后台启动（Linux）
nohup python -m opencode --port 4096 > opencode.log 2>&1 &
```

### 1.4 验证启动

```bash
# 检查服务是否运行
curl http://127.0.0.1:4096

# 预期返回: 服务信息或 404（表示服务已启动）
```

### 1.5 常用配置

```bash
# 查看帮助
python -m opencode --help

# 指定工作目录
python -m opencode --workspace /path/to/workspace

# 启用调试模式
python -m opencode --debug
```

---

## 二、OpenWork 启动

### 2.1 环境要求

- Node.js 18+
- npm 或 yarn

### 2.2 安装步骤

```bash
# 进入 OpenWork 目录
cd /path/to/openwork

# 安装依赖
npm install
# 或
yarn install
```

### 2.3 启动服务

```bash
# 方式1: 开发模式启动（端口 8787）
npm run dev

# 方式2: 生产模式
npm run build
npm start

# 方式3: 后台启动（Linux）
nohup npm run dev > openwork.log 2>&1 &
```

### 2.4 验证启动

```bash
# 检查服务是否运行
curl http://127.0.0.1:8787

# 预期返回: {"code":"not_found","message":"Not found"} 表示服务已启动
```

---

## 三、systemd 服务配置（推荐用于生产环境）

### 3.1 OpenCode systemd 服务

创建文件 `/etc/systemd/system/opencode.service`:

```ini
[Unit]
Description=OpenCode AI Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/opencode
Environment=PATH=/path/to/opencode/venv/bin
ExecStart=/path/to/opencode/venv/bin/python -m opencode --port 4096
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3.2 OpenWork systemd 服务

创建文件 `/etc/systemd/system/openwork.service`:

```ini
[Unit]
Description=OpenWork Skill Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/openwork
Environment=PATH=/usr/bin
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3.3 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动 OpenCode
sudo systemctl enable opencode
sudo systemctl start opencode
sudo systemctl status opencode

# 启动 OpenWork
sudo systemctl enable openwork
sudo systemctl start openwork
sudo systemctl status openwork
```

---

## 四、Docker 启动方式（可选）

### 4.1 OpenCode Docker

```bash
# 运行 OpenCode 容器
docker run -d \
  --name opencode \
  -p 4096:4096 \
  -v /path/to/workspace:/workspace \
  opencode/opencode:latest
```

### 4.2 OpenWork Docker

```bash
# 运行 OpenWork 容器
docker run -d \
  --name openwork \
  -p 8787:8787 \
  openwork/openwork:latest
```

---

## 五、故障排查

### 5.1 端口被占用

```bash
# 查找占用 4096 端口的进程
lsof -i :4096
# 或
netstat -tlnp | grep 4096

# 终止进程
kill -9 <PID>
```

### 5.2 服务无法启动

```bash
# 检查日志
# OpenCode
tail -f /path/to/opencode/opencode.log

# OpenWork
tail -f /path/to/openwork/openwork.log
```

### 5.3 连接测试

```bash
# 测试 OpenCode
curl -v http://127.0.0.1:4096

# 测试 OpenWork
curl -v http://127.0.0.1:8787
```

---

## 六、启动顺序建议

```
1. 启动 OpenCode (端口 4096)
   └─ 等待 5 秒确认启动

2. 启动 OpenWork (端口 8787)
   └─ 等待 5 秒确认启动

3. 启动 AI Portal
   └─ 自动执行前置检查
   └─ 启动后端 (端口 8000)
   └─ 启动前端 (端口 5173)
```

---

## 七、快速启动脚本

创建 `start-all.sh`:

```bash
#!/bin/bash

echo "🚀 启动所有服务..."

# 启动 OpenCode
echo "1. 启动 OpenCode..."
cd /path/to/opencode
source venv/bin/activate
nohup python -m opencode --port 4096 > opencode.log 2>&1 &
sleep 5

# 启动 OpenWork
echo "2. 启动 OpenWork..."
cd /path/to/openwork
nohup npm run dev > openwork.log 2>&1 &
sleep 5

# 启动 AI Portal
echo "3. 启动 AI Portal..."
cd /path/to/agenthub
./scripts/start.sh

echo "✅ 所有服务已启动"
```

赋予执行权限:
```bash
chmod +x start-all.sh
```

---

## 八、验证所有服务

```bash
# 检查所有端口
ss -tlnp | grep -E "4096|8787|8000|5173"

# 或
curl http://127.0.0.1:4096          # OpenCode
curl http://127.0.0.1:8787          # OpenWork
curl http://localhost:8000/api/health  # AI Portal 后端
curl http://localhost:5173          # AI Portal 前端
```

---

## 相关文档

- [02_CONFIGURE_AI_PORTAL.md](./02_CONFIGURE_AI_PORTAL.md) - AI Portal 配置指南
- [03_ADD_WEBSDK_RESOURCES.md](./03_ADD_WEBSDK_RESOURCES.md) - WebSDK 资源配置
