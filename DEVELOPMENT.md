# 开发者指南

本文档提供 AI Portal 的详细开发指南，包括本地开发、测试和调试。

## 目录

- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [测试](#测试)
- [调试](#调试)
- [常见开发任务](#常见开发任务)

## 开发环境设置

### Python 环境设置

```bash
# 确认 Python 版本
/home/yy/python312/bin/python --version

# 安装后端依赖
cd backend
/home/yy/python312/bin/python -m pip install -r requirements.txt
```

### Node.js 环境设置

```bash
# 确认 Node.js 版本
node --version  # 应该是 v22+

# 安装前端依赖
cd frontend
npm install
```

### IDE 配置

#### VSCode

推荐安装以下扩展:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- ESLint (dbaeumer.vscode-eslint)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- TypeScript Vue Plugin (Vue.volar)

#### PyCharm

1. 打开项目根目录
2. 设置 Python 解释器为 `/home/yy/python312/bin/python`
3. 启用 TypeScript 支持

## 代码规范

### Python 代码规范

遵循 PEP 8 规范:

```python
# 好的示例
class MyService:
    """服务类文档字符串"""

    def __init__(self, config: Config):
        self.config = config

    async def process_data(self, data: dict) -> Result:
        """处理数据并返回结果"""
        try:
            # 实现逻辑
            return Result(success=True)
        except Exception as e:
            logger.error(f"处理失败: {e}")
            return Result(success=False, error=str(e))
```

### TypeScript 代码规范

```typescript
// 好的示例
interface UserData {
  id: string;
  name: string;
  email: string;
}

async function fetchUser(userId: string): Promise<UserData | null> {
  try {
    const response = await api.get<UserData>(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('获取用户失败:', error);
    return null;
  }
}
```

### 命名规范

- **Python**:
  - 类名: PascalCase (例如: `UserService`)
  - 函数/变量: snake_case (例如: `get_user`)
  - 常量: UPPER_SNAKE_CASE (例如: `MAX_RETRIES`)

- **TypeScript**:
  - 接口/类型: PascalCase (例如: `UserData`)
  - 函数/变量: camelCase (例如: `getUser`)
  - 常量: UPPER_SNAKE_CASE (例如: `API_BASE_URL`)

## 测试

### 后端测试

```bash
cd backend

# 运行测试 (需要先创建测试文件)
/home/yy/python312/bin/python -m pytest tests/

# 运行特定测试
/home/yy/python312/bin/python -m pytest tests/test_adapters.py

# 生成覆盖率报告
/home/yy/python312/bin/python -m pytest --cov=app tests/
```

### 前端测试

```bash
cd frontend

# 运行测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage
```

### 手动测试

#### 1. 测试模拟登录

```bash
# 访问模拟登录
curl "http://localhost:8000/api/auth/mock-login?emp_no=E10001" -c cookies.txt

# 验证登录
curl http://localhost:8000/api/auth/me -b cookies.txt
```

#### 2. 测试资源列表

```bash
curl http://localhost:8000/api/resources -b cookies.txt
```

#### 3. 测试启动资源

```bash
# 启动通用助手
curl -X POST http://localhost:8000/api/resources/general-chat/launch -b cookies.txt

# 启动知识库
curl -X POST http://localhost:8000/api/resources/kb-policy/launch -b cookies.txt
```

#### 4. 测试发送消息

```bash
# 替换 {session_id} 为实际的会话 ID
curl -X POST http://localhost:8000/api/sessions/{session_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "你好"}' \
  -b cookies.txt
```

## 调试

### 后端调试

#### 使用 Python 调试器

在 VSCode 中创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "envFile": "${workspaceFolder}/backend/.env",
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

#### 使用日志

在代码中添加调试日志:

```python
import logging

logger = logging.getLogger(__name__)

# 调试信息
logger.debug("调试信息: %s", data)

# 一般信息
logger.info("操作完成")

# 警告
logger.warning("警告: 配置未找到")

# 错误
logger.error("错误: %s", str(e), exc_info=True)
```

### 前端调试

#### 使用 React DevTools

1. 安装 React DevTools 浏览器扩展
2. 打开浏览器开发者工具
3. 切换到 React 标签页查看组件树

#### 使用 console

```typescript
console.log('调试信息:', data);
console.warn('警告:', warning);
console.error('错误:', error);

// 表格形式显示对象
console.table(users);

// 分组日志
console.group('用户操作');
console.log('登录');
console.log('获取资源');
console.groupEnd();
```

### API 调试

#### 使用 Swagger UI

访问 `http://localhost:8000/docs` 查看交互式 API 文档。

#### 使用 curl 脚本

创建 `scripts/test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
COOKIE_FILE="cookies.txt"

# 测试健康检查
echo "=== 测试健康检查 ==="
curl $BASE_URL/api/health

# 测试模拟登录
echo -e "\n=== 测试模拟登录 ==="
curl "$BASE_URL/api/auth/mock-login?emp_no=E10001" -c $COOKIE_FILE

# 测试获取用户信息
echo -e "\n=== 测试获取用户信息 ==="
curl $BASE_URL/api/auth/me -b $COOKIE_FILE

# 测试列出资源
echo -e "\n=== 测试列出资源 ==="
curl $BASE_URL/api/resources -b $COOKIE_FILE

echo -e "\n=== 测试完成 ==="
```

## 常见开发任务

### 添加新的 API 端点

1. 在 `backend/app/main.py` 中添加路由:

```python
@app.get("/api/my-endpoint")
async def my_endpoint(user: CurrentUser):
    """我的新端点"""
    return {"message": "Hello", "user": user.name}
```

2. 在 `frontend/src/api.ts` 中添加客户端方法:

```typescript
export const myApi = {
  getMyData: () =>
    api.get<any>('/api/my-endpoint'),
};
```

### 添加新页面

1. 在 `frontend/src/components/` 中创建组件:

```typescript
// MyPage.tsx
export function MyPage() {
  return (
    <div>
      <h1>我的新页面</h1>
    </div>
  );
}
```

2. 在 `frontend/src/App.tsx` 中添加路由:

```tsx
<Route path="/my-page" element={<MyPage />} />
```

### 修改资源配置

编辑 `backend/config/resources.json`:

```json
{
  "id": "new-resource",
  "name": "新资源",
  "type": "skill_chat",
  "launch_mode": "native",
  "group": "技能助手",
  "description": "资源描述",
  "enabled": true,
  "tags": ["new"],
  "config": {
    "skill_name": "new_skill",
    "workspace_id": "default"
  }
}
```

### 自定义认证

1. 编辑 `backend/app/auth/service.py`:

```python
class AuthService:
    async def resolve_sso_user(self, code: str) -> Optional[UserCtx]:
        # 调用真实 SSO API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://your-sso.com/oauth/token",
                data={"code": code}
            )
            user_data = response.json()
            return UserCtx(**user_data)
```

### 自定义访问控制

1. 编辑 `backend/app/acl/service.py`:

```python
class ACLService:
    def check_resource_access(
        self,
        resource: Resource,
        user: UserCtx
    ) -> bool:
        # 自定义访问逻辑
        if resource.id == "admin-only":
            return "admin" in user.roles
        return True
```

## 性能优化

### 后端优化

1. **使用异步操作**: 所有 I/O 操作使用 async/await
2. **连接池**: HTTPX 自动使用连接池
3. **缓存**: 缓存不常变化的数据

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_resources():
    return catalog_service.get_resources()
```

### 前端优化

1. **代码分割**: 使用 React.lazy
2. **记忆化**: 使用 useMemo, useCallback
3. **虚拟化**: 大列表使用 react-window

```typescript
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});
```

## 故障排除

### 问题: 无法连接到 OpenCode

**解决方案**:
1. 检查 OpenCode 是否正在运行
2. 验证 URL 和端口配置
3. 检查 CORS 设置

### 问题: 前端无法访问 API

**解决方案**:
1. 检查 Vite proxy 配置
2. 验证 CORS 设置
3. 查看浏览器控制台错误

### 问题: 会话数据丢失

**解决方案**:
1. 检查是否使用内存存储
2. 考虑切换到 Redis 存储
3. 检查存储服务是否正常

## 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/my-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/my-feature`
5. 创建 Pull Request

## 发布流程

1. 更新版本号
2. 更新 CHANGELOG
3. 创建 Git 标签
4. 构建生产版本
5. 部署到生产环境

```bash
# 后端
cd backend
/home/yy/python312/bin/python -m build

# 前端
cd frontend
npm run build
```
