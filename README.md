# Rainbow 桌宠 🖥️🐾

一个基于 Python/Tkinter 的 Windows 桌面宠物应用，支持 AI 对话、自动行走、聊天气泡等功能。

## 功能

- **桌面动画** — 24 组 GIF 动画循环播放，宠物栩栩如生
- **拖拽移动** — 鼠标拖拽宠物任意放置
- **自动行走** — 宠物在桌面上随机走动，可配置速度和开关
- **AI 主动聊天** — 定时主动说话，支持 OpenAI / Claude / DeepSeek 等多种 API
- **手动聊天** — 按快捷键（默认 Q）打开聊天框与宠物对话
- **联网搜索** — 聊天时可开启联网搜索，获取实时信息
- **聊天气泡** — 对话内容以气泡形式显示在宠物头顶
- **配置面板** — 图形化界面调整大小、速度、API 设置、气泡颜色等
- **网页版** — `index.html` 提供浏览器端桌宠体验

## 快速开始

### 方式一：运行 exe（推荐）

双击 `启动桌宠.bat` 或运行 `dist/Rainbow桌宠.exe`。

### 方式二：运行源码

```bash
pip install pillow
python pet.py
```

### 方式三：网页版

用浏览器打开 `index.html`。

## 配置

首次运行后会在程序目录生成 `pet_config.json`，可在配置面板中修改：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `api_provider` | API 提供商 (openai/claude/deepseek) | openai |
| `api_key` | API 密钥 | - |
| `api_model` | 模型名称 | gpt-4o-mini |
| `api_base` | API 地址 | https://api.openai.com/v1 |
| `api_system_prompt` | 人格设定提示词 | 你是一个可爱的桌宠... |
| `size` | 宠物大小 (px) | 120 |
| `speed` | 移动速度 | 3 |
| `auto_walk` | 是否自动行走 | true |
| `proactive_chat` | 是否主动聊天 | false |
| `proactive_interval` | 主动聊天间隔 (秒) | 60 |
| `chat_key` | 聊天快捷键 | c |

## 快捷键

- **Q** — 打开/关闭聊天框
- **鼠标悬停** — 随机说话
- **鼠标拖拽** — 移动宠物

## 开发

### 打包 exe

```bash
pip install pyinstaller pillow
pyinstaller Rainbow桌宠.spec
```

## 技术栈

- Python 3.9 + Tkinter
- Pillow (GIF 处理)
- PyInstaller (打包)
- HTML/CSS/JavaScript (网页版)

## 许可证

MIT

---

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)。
