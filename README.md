# ComicManager Neo - CBZ/ZIP 文件合并工具

一个功能强大的桌面应用程序，用于合并多个 CBZ（Comic Book ZIP）和 ZIP 文件。采用现代 Web 技术栈构建，提供流畅的用户体验和美观的界面。

## 功能特性

### 核心功能
- **多格式支持**: 同时处理 CBZ 和 ZIP 文件格式
- **智能图片提取**: 从 ZIP 文件中自动提取图片（JPG, PNG, WEBP, GIF, BMP）
- **自动重命名**: 按章节自动重命名图片（ch1_001.jpg, ch2_001.jpg...）
- **多文件合并**: 支持同时合并多个漫画文件
- **元数据保留**: 可选择保留原始文件的 ComicInfo.xml 元数据

### 用户体验
- **拖拽排序**: 直观的文件顺序调整功能
- **键盘操作**: 丰富的键盘快捷键支持
- **进度显示**: 实时显示合并进度
- **主题切换**: 支持浅色/深色主题
- **响应式设计**: 适配不同屏幕尺寸
- **Toast 通知**: 完善的成功/错误提示
- **配置持久化**: 自动保存用户设置（YAML 格式）

## 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **后端** | Python | 3.10+ | 核心应用程序逻辑 |
| **后端框架** | FastAPI | latest | 本地 HTTP API 服务器 |
| **前端容器** | PyWebView | 6.x | 桌面 WebView 封装 |
| **前端框架** | Vue 3 | latest | 响应式 UI 框架 |
| **构建工具** | Vite | latest | 前端构建工具链 |
| **CSS 框架** | TailwindCSS | latest | 实用优先的 CSS |
| **UI 组件库** | DaisyUI | latest | TailwindCSS 组件库 |
| **Python 包管理** | uv | latest | Python 依赖管理 |
| **Node 包管理** | bun | latest | 前端依赖管理 |
| **打包工具** | PyInstaller | latest | 独立可执行文件构建 |
| **配置格式** | YAML | - | 应用配置格式 |

## 系统要求

- Python 3.10+
- Node.js 18+ (用于前端开发)
- uv 包管理器
- bun 包管理器 (可选，用于前端)
- 支持的操作系统：Windows, macOS, Linux

## 安装和运行

在Release页面下载最新压缩包，解压后进入项目目录，运行EXE可执行文件。

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/wish2333/comicmanager.git
cd comicmanager-neo

# 确保已安装 uv 包管理器
# 如果没有安装，请访问 https://github.com/astral-sh/uv
```

### 2. 安装后端依赖

```bash
# 使用 uv 安装依赖（配置清华镜像源）
uv sync --default-index https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 安装前端依赖

```bash
# 进入前端目录
cd frontend

# 使用 bun 或 npm 安装依赖
bun install
# 或
npm install

# 返回项目根目录
cd ..
```

### 4. 运行程序

#### 开发模式

```bash
# 启动开发服务器（后端 + 前端热重载）
uv run python src/main.py --dev
```

#### 生产模式

```bash
# 构建前端
cd frontend
bun run build
cd ..

# 启动应用
uv run python src/main.py
```

### 5. 打包为可执行文件

```bash
# 使用 PyInstaller 打包
uv run build.py

# 打包后的文件位于 dist/ 目录
```

## 使用方法

### 基本操作

1. **添加文件**:
   - 点击"添加文件"按钮，或使用快捷键 `Ctrl+O`
   - 选择要合并的 CBZ 和 ZIP 文件（支持多选）
   - 直接拖拽文件到窗口内

2. **调整顺序**:
   - **拖拽方式**: 直接拖拽文件到目标位置
   - **按钮方式**: 选中文件后使用上移/下移/置顶/置底按钮
   - **键盘方式**: 选中文件后使用 `Ctrl+↑/↓/Home/End`

3. **设置输出**:
   - 输入输出文件名（默认自动生成）
   - 选择保存目录
   - 可选择是否保留原始元数据
   - 选择要提取的图片格式

4. **开始合并**:
   - 点击"开始合并"按钮
   - 观察进度条显示
   - 合并完成后查看结果

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 添加文件 |
| `Ctrl+A` | 全选文件 |
| `Delete` | 删除选中文件 |
| `Ctrl+↑` | 向上移动选中项 |
| `Ctrl+↓` | 向下移动选中项 |
| `Ctrl+Home` | 移至顶部 |
| `Ctrl+End` | 移至底部 |
| `Ctrl+Q` | 退出程序 |

### 文件选择

- **单选**: 直接点击文件
- **多选**: `Ctrl+点击` 添加/移除文件
- **范围选择**: `Shift+点击` 选择范围

## 项目结构

```
comicmanager-neo/
├── src/                       # 后端代码
│   ├── main.py               # 程序入口
│   ├── server.py             # FastAPI 应用工厂
│   ├── js_api.py             # PyWebView JS API
│   ├── core/                 # 核心功能模块
│   │   ├── config.py         # 配置管理
│   │   ├── constants.py      # 常量定义
│   │   └── state.py          # 应用状态
│   ├── models/               # 数据模型
│   │   ├── files.py          # 文件模型
│   │   ├── progress.py       # 进度模型
│   │   └── settings.py       # 设置模型
│   ├── routes/               # API 路由
│   │   ├── browse.py         # 文件浏览
│   │   ├── files.py          # 文件管理
│   │   ├── formats.py        # 格式支持
│   │   ├── health.py         # 健康检查
│   │   ├── merge.py          # 合并操作
│   │   └── settings.py       # 设置管理
│   ├── services/             # 业务服务
│   │   ├── extractor.py      # ZIP 提取器
│   │   ├── file_info.py      # 文件信息
│   │   ├── merger.py         # 合并服务
│   │   └── validator.py      # 文件验证
│   └── tasks/                # 后台任务
│       └── merge_task.py     # 合并任务
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── main.ts           # 前端入口
│   │   ├── App.vue           # 根组件
│   │   ├── api/              # API 客户端
│   │   ├── components/       # Vue 组件
│   │   ├── composables/      # 组合式函数
│   │   ├── styles/           # 样式文件
│   │   └── types/            # TypeScript 类型
│   ├── index.html            # HTML 模板
│   ├── package.json          # 前端依赖
│   ├── vite.config.ts        # Vite 配置
│   └── tailwind.config.js    # TailwindCSS 配置
├── docs/                     # 项目文档
│   ├── PRD-2026-03-29.md     # 产品需求文档（英文）
│   └── PRD-zh-2026-03-29.md  # 产品需求文档（中文）
├── config.yaml               # 默认配置文件
├── pyproject.toml            # Python 项目配置
├── comicmanager_neo.spec     # PyInstaller 配置
└── build.py                  # 构建脚本
```

## 配置

应用程序支持多种配置选项，配置文件采用 YAML 格式：

- **默认输出目录**: 设置文件保存位置
- **界面主题**: 选择浅色/深色主题
- **图片格式**: 选择要提取的图片格式
- **最近文件**: 记住最近使用的文件
- **窗口状态**: 记住窗口大小和位置

配置文件位置：`~/.comicmanager/config.yaml`

## API 端点

### 文件管理
- `POST /api/files` - 添加文件到合并队列
- `GET /api/files` - 获取队列中的所有文件
- `DELETE /api/files` - 从队列移除文件
- `PUT /api/files/reorder` - 重新排序文件列表
- `POST /api/files/validate` - 验证文件

### 合并操作
- `POST /api/merge` - 启动合并操作
- `GET /api/progress/{task_id}` - 获取合并进度（SSE）

### 设置管理
- `GET /api/settings` - 获取应用设置
- `PUT /api/settings` - 更新设置

### 其他
- `GET /api/formats` - 获取支持的图片格式
- `POST /api/browse` - 打开文件/目录选择器
- `GET /api/health` - 健康检查

## 故障排除

### 常见问题

1. **启动失败**:
   ```bash
   # 检查 Python 版本
   python --version  # 需要 >= 3.10

   # 检查依赖安装
   uv show fastapi uvicorn pywebview
   ```

2. **前端构建失败**:
   ```bash
   # 进入前端目录
   cd frontend

   # 清理缓存并重新安装
   rm -rf node_modules
   bun install

   # 重新构建
   bun run build
   ```

3. **打包失败**:
   ```bash
   # 确保 PyInstaller 已安装
   uv add --dev pyinstaller

   # 检查 spec 文件配置
   cat comicmanager_neo.spec
   ```

4. **合并失败**:
   - 检查输入 CBZ 文件是否完整
   - 确认输出目录有写入权限
   - 查看应用日志了解具体问题

### 依赖安装问题

如果遇到依赖安装问题，可以尝试以下方法：

```bash
# 方法1: 升级 uv
pip install --upgrade uv

# 方法2: 清理缓存
uv cache clean

# 方法3: 重新创建虚拟环境
uv venv --force
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
```

## 开发

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd comicmanager-neo

# 安装后端依赖
uv sync

# 安装前端依赖
cd frontend
bun install
cd ..
```

### 开发模式运行

```bash
# 启动开发服务器（后端 + 前端热重载）
uv run python src/main.py --dev
```

### 代码规范

项目遵循以下代码规范：

- **Python**: 遵循 PEP 8 规范
- **TypeScript**: 使用 ESLint 进行代码检查
- **Vue**: 遵循 Vue 3 风格指南

```bash
# Python 代码格式化（如果安装了 black）
uv run black src/

# TypeScript 类型检查
cd frontend
bun run type-check
```

## 更新日志

### v1.0.0 (2026-03-29)
- **全新架构**: 使用 FastAPI + Vue 3 + PyWebView 重构
- **现代化 UI**: 采用 TailwindCSS + DaisyUI 构建美观界面
- **实时进度**: 使用 SSE 实现实时进度更新
- **主题支持**: 支持浅色/深色主题切换
- **YAML 配置**: 使用 YAML 替代 JSON 配置格式
- **响应式设计**: 适配不同屏幕尺寸
- **独立打包**: 支持 PyInstaller 打包为独立可执行文件

### v0.2.0 (2025-11-30)
- **新增ZIP文件支持**: 完整支持ZIP格式的漫画文件
- **智能图片提取**: 从ZIP文件中自动提取图片并按格式过滤
- **自动重命名系统**: 按章节自动重命名图片（ch1_001.jpg, ch2_001.jpg...）
- **增强的文件验证**: 改进的文件格式检查和错误处理
- **性能优化**: 更高效的图片提取和重命名流程

### v0.1.0 (2025-11-29)
- 初始版本发布（Tkinter 版本）
- 基础CBZ文件合并功能
- 拖拽排序支持
- 进度显示
- 配置管理

## 许可证

本项目采用 MIT 许可证。

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue 3](https://vuejs.org/) - 渐进式 JavaScript 框架
- [PyWebView](https://pywebview.flowrl.com/) - 轻量级跨平台 WebView 封装
- [TailwindCSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- [DaisyUI](https://daisyui.com/) - 基于 TailwindCSS 的组件库

## 支持

如果您遇到问题或有建议：

1. 查看故障排除部分
2. 检查是否为已知问题
3. 创建新的 Issue 并描述问题
4. 提供详细的错误信息和复现步骤

---

感谢使用 ComicManager Neo！
