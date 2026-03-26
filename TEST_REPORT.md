# Test Report（文档整理后）

## 1. 目的

本报告用于说明当前仓库推荐的测试入口与验收标准，替代旧版“单次跑分式”报告。

---

## 2. 推荐测试矩阵

### 后端 API
- 健康检查：`/api/health`
- 认证链路：`/api/auth/mock-login`、`/api/auth/me`、`/api/auth/logout`
- 资源链路：`/api/resources`、`/api/resources/grouped`、`/api/resources/{id}`、`/launch`
- 会话链路：`/api/sessions`、`/api/sessions/{id}/messages`
- WebSDK 链路：`/api/launches`、`/api/launches/{id}/embed-config`
- Skill 链路：`/api/skills`

### 前端
- 首页分组展示
- native 资源启动与聊天
- websdk 资源启动与宿主页渲染
- 登录态失效自动跳转

---

## 3. 自动化入口

```bash
# 后端简测
cd backend && /home/yy/python312/bin/python tests/test_api_simple.py

# 后端完整版
cd backend && /home/yy/python312/bin/python tests/test_api.py

# 综合脚本
./scripts/test.sh
```

---

## 4. 验收基线（V1）

1. native/skill 资源可以创建并列出会话。
2. 发送消息后 `updated_at` 会刷新，侧栏排序可反映“最近活跃”。
3. websdk 资源只记录 launch，不生成 portal session。
4. `sdk-host.html` 能根据 embed config 正确加载 SDK。
5. 所有接口都可在 `/docs` 查看。

---

## 5. 历史结果

历史测试快照保存在：
- [TEST_RESULTS_2026-03-26.md](TEST_RESULTS_2026-03-26.md)
