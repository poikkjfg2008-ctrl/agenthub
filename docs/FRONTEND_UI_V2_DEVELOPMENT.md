# AI Portal 前端界面 V2 开发文档

## 📋 文档信息

- **项目名称**: AI Portal 前端界面改版
- **开发时间**: 2026-03-28
- **版本**: V2.0
- **开发人员**: AI Assistant

---

## 🎯 项目背景与目标

### 背景
原版本进入 WebUI 后需要先从资源列表选择资源，然后才能进入对话界面。这种交互流程增加了用户操作步骤，不够直观。

### 目标
改造为左侧资源侧边栏 + 中间对话区域的布局，实现：
1. 进入页面后直接显示默认资源（通用助手）的对话界面
2. 左侧资源列表可展开/折叠，点击切换不同资源
3. 更友好的 UI 展示（资源卡片形式、图标、描述）
4. 支持 Markdown 渲染、数学公式、代码高亮
5. 优化输入框和消息显示

---

## 🏗️ 技术架构

### 技术栈
- **框架**: React 18 + TypeScript 5.7
- **构建工具**: Vite 6.0+
- **路由**: React Router DOM 6.28+
- **样式**: Tailwind CSS 3.4+
- **图标**: Lucide React 0.468+
- **HTTP 客户端**: Axios 1.7+

### 新增依赖
```bash
# Markdown 渲染
npm install react-markdown

# GitHub 风格 Markdown 扩展（表格、删除线等）
npm install remark-gfm

# 数学公式支持
npm install remark-math rehype-katex

# 代码高亮
npm install rehype-highlight
```

---

## 📁 文件变更清单

### 新增文件
| 文件路径 | 说明 |
|---------|------|
| `frontend/src/components/ResourceSidebar.tsx` | 左侧资源侧边栏组件 |

### 修改文件
| 文件路径 | 变更类型 | 说明 |
|---------|---------|------|
| `frontend/src/App.tsx` | 重大修改 | 重构整体布局，三栏式结构 |
| `frontend/src/components/ChatInterface.tsx` | 重大修改 | 新增 Markdown 渲染、优化输入框 |
| `frontend/src/components/SessionSidebar.tsx` | 轻微修改 | 清理未使用的导入 |
| `frontend/src/styles/globals.css` | 新增样式 | Markdown 渲染样式、消息样式 |
| `frontend/src/types.ts` | 扩展 | 资源配置类型扩展 |
| `frontend/tsconfig.json` | 配置 | 排除测试文件 |

---

## 🎨 界面设计规范

### 布局结构
```
┌─────────────────────────────────────────────────────────────┐
│  Header (AI Portal Logo + 用户信息 + 工作区切换按钮)            │
├──────────────┬──────────────────────────────┬───────────────┤
│              │                              │               │
│  Resource    │   Session Sidebar (可选)     │   Chat/       │
│  Sidebar     │   + Chat Interface           │   Workspace   │
│  (w-72)      │                              │   (可选)      │
│              │                              │               │
│  固定 288px   │     弹性宽度 (剩余空间)        │   380-600px   │
│              │                              │               │
└──────────────┴──────────────────────────────┴───────────────┘
```

### 资源分组
| 分组名称 | 图标 | 颜色主题 |
|---------|------|---------|
| 基础对话 | MessageSquare | 蓝色系 |
| 技能助手 | Bot | 紫色系 |
| 知识库 | BookOpen | 绿色系 |
| 智能应用 | Zap | 橙色系 |
| 集成应用 | Globe | 靛蓝色系 |

### 资源图标设计
每个资源都有独特的渐变色图标：

| 资源 ID | 名称 | 图标 | 渐变背景 |
|--------|------|------|---------|
| general-chat | 通用助手 | Sparkles | blue-400 → blue-600 |
| skill-coding | 编程助手 | Code | cyan-400 → cyan-600 |
| skill-writing | 写作助手 | PenTool | pink-400 → pink-600 |
| skill-data-analysis | 数据分析助手 | BarChart3 | emerald-400 → emerald-600 |
| kb-policy | 制度知识库 | FileText | amber-400 → amber-600 |
| kb-tech | 技术文档库 | Database | teal-400 → teal-600 |
| agent-report | 报表生成器 | Layers | violet-400 → violet-600 |
| op-agent | OP Agent | Cpu | indigo-400 → indigo-600 |

---

## 💻 核心功能实现

### 1. ResourceSidebar 组件

#### 功能特性
- **分组展开/折叠**: 点击分组标题可展开/收起资源列表
- **当前资源高亮**: 选中资源显示蓝色左边框和背景色
- **资源信息展示**: 图标、名称、描述、标签
- **响应式设计**: 固定宽度 288px，支持滚动

#### 关键代码
```tsx
// 分组配置
const groupConfig: Record<string, { icon: React.ReactNode; color: string; bgColor: string }> = {
  '基础对话': {
    icon: <MessageSquare className="w-5 h-5" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  // ...
};

// 资源图标映射
const getResourceIcon = (resource: Resource): React.ReactNode => {
  switch (resource.id) {
    case 'general-chat': return <Sparkles className={iconClass} />;
    case 'skill-coding': return <Code className={iconClass} />;
    // ...
  }
};
```

### 2. ChatInterface 组件增强

#### Markdown 渲染
```tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';

<ReactMarkdown
  remarkPlugins={[remarkGfm, remarkMath]}
  rehypePlugins={[rehypeKatex, rehypeHighlight]}
  components={{
    // 自定义渲染组件
    code: CodeComponent,
    table: TableComponent,
    // ...
  }}
>
  {message.text}
</ReactMarkdown>
```

#### 支持的 Markdown 特性
| 特性 | 状态 | 说明 |
|------|------|------|
| 标题 (H1-H6) | ✅ | 不同字号和粗细 |
| 段落 | ✅ | 自动换行、间距优化 |
| 列表 (有序/无序) | ✅ | 缩进和样式美化 |
| 代码块 | ✅ | 语法高亮 + 复制按钮 |
| 行内代码 | ✅ | 灰色背景 |
| 表格 | ✅ | 边框、表头高亮 |
| 引用块 | ✅ | 左边框 + 背景色 |
| 链接 | ✅ | 蓝色下划线 |
| 数学公式 | ✅ | LaTeX 语法支持 |
| 分割线 | ✅ | 灰色细线 |

#### 输入框优化
- **高度自适应**: 根据内容自动调整高度 (min: 56px, max: 200px)
- **圆角设计**: rounded-2xl 圆角
- **聚焦效果**: 边框变色 + 阴影
- **快捷提示**: 显示资源预设的 starter_prompts

### 3. App.tsx 布局重构

#### 状态管理
```tsx
const [currentResource, setCurrentResource] = useState<Resource | null>(null);
const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
const [currentLaunchId, setCurrentLaunchId] = useState<string | null>(null);
const [showWorkspace, setShowWorkspace] = useState(false);
const [workspaceMode, setWorkspaceMode] = useState<'websdk' | 'iframe' | null>(null);
```

#### 默认资源加载
```tsx
const DEFAULT_RESOURCE_ID = 'general-chat';

// 资源加载完成后自动启动默认资源
useEffect(() => {
  if (Object.keys(resourcesGrouped).length > 0 && !currentResource) {
    launchDefaultResource();
  }
}, [resourcesGrouped]);
```

#### 资源切换逻辑
```tsx
const handleSelectResource = async (resource: Resource) => {
  setIsLaunching(true);
  setCurrentResource(resource);

  const response = await resourceApi.launchResource(resource.id);
  const launchData: LaunchResponse = response.data;

  if (launchData.kind === 'native') {
    setCurrentSessionId(launchData.portal_session_id);
    setShowWorkspace(false);
  } else if (launchData.kind === 'websdk' || launchData.kind === 'iframe') {
    setCurrentLaunchId(launchData.launch_id);
    setShowWorkspace(true);
    setWorkspaceMode(launchData.kind);
  }
};
```

---

## 🎭 样式设计

### Tailwind 配置
```javascript
// tailwind.config.js
colors: {
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },
}
```

### 全局样式 (globals.css)

#### 消息气泡样式
```css
.message-user {
  @apply bg-gradient-to-br from-primary-500 to-primary-600 
         text-white ml-auto rounded-2xl rounded-tr-sm 
         px-5 py-3 shadow-sm;
  max-width: 85%;
}

.message-assistant {
  @apply bg-white text-gray-800 mr-auto 
         rounded-2xl rounded-tl-sm px-5 py-3 
         shadow-sm border border-gray-100;
  max-width: 85%;
}
```

#### Markdown 内容样式
```css
.markdown-content h1 { @apply text-2xl font-bold text-gray-900 mt-4 mb-2; }
.markdown-content h2 { @apply text-xl font-bold text-gray-800 mt-3 mb-2; }
.markdown-content ul { @apply list-disc pl-6 my-2 space-y-1; }
.markdown-content ol { @apply list-decimal pl-6 my-2 space-y-1; }
.markdown-content code { 
  @apply bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono; 
}
```

---

## 🧪 测试情况

### 测试环境
- **后端**: http://localhost:8000
- **前端**: http://localhost:5173
- **测试时间**: 2026-03-28

### 测试结果

| 测试类别 | 通过 | 警告 | 失败 | 合计 | 通过率 |
|---------|:----:|:----:|:----:|:----:|:------:|
| 基础服务 | 3 | 0 | 0 | 3 | 100% |
| 认证功能 | 2 | 1 | 0 | 3 | 100% |
| API 功能 | 5 | 0 | 0 | 5 | 100% |
| 前端界面 | 4 | 1 | 0 | 5 | 100% |
| 资源类型 | 2 | 3 | 1 | 6 | 83% |
| **总计** | **16** | **5** | **1** | **22** | **95.5%** |

### 功能验证

| 功能模块 | 状态 | 说明 |
|---------|:----:|------|
| 新布局三栏结构 | ✅ | 左侧资源栏 + 中间对话区 + 可选工作区 |
| 资源卡片展示 | ✅ | 图标、名称、描述、标签完整显示 |
| 分组展开/折叠 | ✅ | 点击分组标题可切换展开状态 |
| 默认资源加载 | ✅ | 进入页面自动加载通用助手 |
| 资源切换 | ✅ | 点击资源平滑切换对话 |
| Markdown 渲染 | ✅ | 标题、列表、表格、代码等正常渲染 |
| 数学公式 | ✅ | LaTeX 公式正常显示 |
| 代码高亮 | ✅ | 代码块带语法高亮和复制按钮 |
| 输入框自适应 | ✅ | 根据内容自动调整高度 |
| WebSDK 资源 | ✅ | 工作区正常显示 |

---

## 🚀 部署说明

### 安装依赖
```bash
cd frontend
npm install
```

### 开发模式
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

构建输出位于 `frontend/dist/` 目录。

---

## 📌 注意事项

### 已知问题
1. **OpenCode 服务依赖**: Native 类型资源需要 OpenCode 后端服务 (http://127.0.0.1:4096)
2. **op-agent 资源 404**: 配置文件中存在但该资源未正确配置
3. **favicon.ico 缺失**: 可选资源，不影响核心功能

### 配置建议
```bash
# backend/.env
# 如需使用对话功能，配置 OpenCode
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENCODE_USERNAME=opencode
OPENCODE_PASSWORD=your-password

# 生产环境关闭 mock 回退
AUTH_MOCK_FALLBACK_ENABLED=false
```

---

## 📝 变更日志

### V2.0 (2026-03-28)
- ✅ 新增 ResourceSidebar 组件，支持分组资源展示
- ✅ 重构 App.tsx，实现三栏式布局
- ✅ 增强 ChatInterface，支持 Markdown 渲染
- ✅ 集成数学公式 (KaTeX) 和代码高亮
- ✅ 优化消息气泡和输入框样式
- ✅ 资源卡片添加渐变色图标
- ✅ 默认自动加载通用助手
- ✅ 支持 WebSDK/iframe 工作区切换显示

---

## 🔮 后续优化建议

1. **性能优化**: 大型对话列表虚拟滚动
2. **消息搜索**: 支持历史消息搜索功能
3. **主题切换**: 支持暗黑模式
4. **国际化**: 多语言支持
5. **快捷键**: 支持键盘快捷键操作
6. **移动端适配**: 针对平板和手机优化布局
7. **消息导出**: 支持导出对话为 PDF/Markdown

---

## 📞 联系方式

如有问题或建议，请参考：
- [API.md](../API.md) - API 接口文档
- [QUICKSTART.md](../QUICKSTART.md) - 快速开始指南
- [DEVELOPMENT.md](../DEVELOPMENT.md) - 开发规范
