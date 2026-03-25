# AI Portal 快速开始指南

5 分钟快速启动 AI Portal。

## 前置条件检查

```bash
# 检查 Python
/home/yy/python312/bin/python --version  # 应该显示 Python 3.12.x

# 检查 Node.js
node --version  # 应该显示 v22.x.x

# 检查 OpenCode (应该已安装)
opencode --version

# 检查 OpenWork (应该已安装)
openwork --version
```

## 一键启动 (推荐)

```bash
# 使用启动脚本
./scripts/start.sh
```

启动脚本会自动:
1. 检查环境和依赖
2. 创建配置文件
3. 启动后端服务 (端口 8000)
4. 启动前端服务 (端口 5173)

## 手动启动

### 1. 安装依赖

```bash
# 后端依赖
cd backend
/home/yy/python312/bin/python -m pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example backend/.env

# 编辑配置 (可选，使用默认值也可以)
vim backend/.env
```

### 3. 启动外部服务

在两个独立的终端中启动:

```bash
# 终端 1: 启动 OpenCode
opencode serve --port 4096 --cors-origin=http://localhost:8000 --server-password=your-password

# 终端 2: 启动 OpenWork
openwork serve --workspace /path/to/workspace --daemon-port 8787
```

### 4. 启动 AI Portal

```bash
# 终端 3: 启动后端
cd backend
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端 4: 启动前端
cd frontend
npm run dev
```

## 访问应用

打开浏览器访问: **http://localhost:5173**

### 首次登录

系统会自动跳转到模拟登录页面，使用默认员工号 `E10001` 登录。

手动访问登录页面:
```
http://localhost:8000/api/auth/mock-login?emp_no=E10001
```

## 快速测试

### 1. 测试 API 健康检查

```bash
curl http://localhost:8000/api/health
```

应该返回:
```json
{
  "status": "healthy",
  "portal_name": "AI Portal",
  "version": "1.0.0"
}
```

### 2. 测试模拟登录

```bash
curl "http://localhost:8000/api/auth/mock-login?emp_no=E10001" -c cookies.txt
```

### 3. 测试列出资源

```bash
curl http://localhost:8000/api/resources -b cookies.txt
```

### 4. 测试启动资源

```bash
curl -X POST http://localhost:8000/api/resources/general-chat/launch -b cookies.txt
```

### 5. 查看 API 文档

访问: **http://localhost:8000/docs**

## 主要功能演示

### 1. 浏览资源

登录后，你会看到按类别分组的资源:
- 📝 **基础对话**: 通用助手
- 🤖 **技能助手**: 编程、写作、数据分析
- 📚 **知识库**: 制度、技术文档
- 🎯 **智能应用**: 报表生成器

### 2. 原生对话

1. 点击 "通用助手" 的 "启动" 按钮
2. 进入聊天界面
3. 输入消息并发送
4. 查看侧边栏的会话历史

### 3. 技能对话

1. 返回首页
2. 点击 "编程助手" 的 "启动" 按钮
3. 使用技能特定的提示词
4. 体验技能增强的对话

### 4. WebSDK 应用

1. 返回首页
2. 点击 "制度知识库" 的 "启动" 按钮
3. 查看 iframe 嵌入的知识库界面
4. 体验无缝集成

## 停止服务

### 使用停止脚本 (推荐)

```bash
./scripts/stop.sh
```

### 手动停止

```bash
# 停止后端 (Ctrl+C 或)
pkill -f "uvicorn app.main:app"

# 停止前端 (Ctrl+C 或)
pkill -f "vite"
```

## 故障排除

### 问题 1: 端口已被占用

```bash
# 检查端口占用
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口

# 杀死占用进程
kill -9 <PID>
```

### 问题 2: Python 依赖安装失败

```bash
# 升级 pip
/home/yy/python312/bin/python -m pip install --upgrade pip

# 清除缓存重新安装
/home/yy/python312/bin/python -m pip install --no-cache-dir -r backend/requirements.txt
```

### 问题 3: 前端依赖安装失败

```bash
# 清除 node_modules 重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 问题 4: 无法连接到 OpenCode

```bash
# 检查 OpenCode 是否运行
curl http://localhost:4096/api/health

# 如果未运行，启动 OpenCode
opencode serve --port 4096 --cors-origin=http://localhost:8000 --server-password=your-password
```

### 问题 5: CORS 错误

确保 `backend/app/config.py` 中的 `cors_origins` 包含前端地址:

```python
cors_origins: list = [
    "http://localhost:5173",
    "http://localhost:8000",
]
```

## 下一步

1. **阅读完整文档**: 查看 [README.md](README.md) 了解详细功能
2. **查看 API 文档**: 访问 [API.md](API.md) 了解所有 API
3. **开发指南**: 查看 [DEVELOPMENT.md](DEVELOPMENT.md) 了解如何开发
4. **自定义配置**: 编辑 `backend/config/resources.json` 添加自己的资源

## 生产部署

生产环境部署需要:

1. 使用 Redis 存储 (设置 `USE_REDIS=true`)
2. 配置真实的 SSO 集成
3. 使用 HTTPS
4. 配置防火墙和安全组
5. 设置监控和日志收集

详见 [README.md](README.md) 的部署指南部分。

## 获取帮助

- 查看日志: `tail -f logs/backend.log` 或 `tail -f logs/frontend.log`
- API 文档: http://localhost:8000/docs
- GitHub Issues: (项目地址)

## 常用命令

```bash
# 启动所有服务
./scripts/start.sh

# 停止所有服务
./scripts/stop.sh

# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log

# 重启服务
./scripts/stop.sh && ./scripts/start.sh

# 检查服务状态
curl http://localhost:8000/api/health
```

## 配置文件位置

- 后端配置: `backend/.env`
- 前端配置: `frontend/.env`
- 资源目录: `backend/config/resources.json`
- OpenCode 配置: OpenCode 服务器配置
- OpenWork 配置: OpenWork 服务器配置

## 环境变量参考

主要环境变量:

```bash
# 服务端口
PORT=8000

# 存储模式
USE_REDIS=false  # true 表示使用 Redis

# JWT 密钥
JWT_SECRET=your-secret-key

# OpenCode 配置
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENCODE_PASSWORD=your-password

# OpenWork 配置
OPENWORK_BASE_URL=http://127.0.0.1:8787
```

完成! 🎉 你现在可以开始使用 AI Portal 了。
