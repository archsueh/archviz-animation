---
name: archviz-animationd
description: |
  技术架构动态图全流程：内容分析 → JSON spec 构建 → Python 渲染 → 三交付物（.excalidraw 可编辑源 + PNG 静态图 + GIF 动画）。
  黑底手绘风格，glow 流光 + pulse 模块动效，无需 image API，纯代码生成，结果完全确定可复现。
  触发词：动态架构图、animated diagram、架构动画、excalidraw、技术图动效、gif 架构图
tags: [architecture, diagram, animated, excalidraw, gif, python, hand-drawn]
version: 0.1.0
author: archsueh
license: MIT
---

# Archviz Animated Pipeline

黑底手绘风格技术架构动态图，三交付物全流程。依赖：`pip install Pillow>=10.0.0`

---

## 架构

```
[1] 内容分析 ← 理解技术架构 / 文章 / 需求
     ↓
[2] JSON Spec 构建 ← 填充固定布局区的内容
     ↓
[3] Python 渲染 ← scripts/render_animated_diagram.py
     ↓
[4] 验证 ← --verify（帧差） + --check（尺寸/帧数/ID唯一性）
     ↓
[5] 交付 ← .excalidraw + PNG + GIF
```

---

## [1] 内容分析

从用户输入提取：

| 字段 | 说明 |
|---|---|
| `title.prefix` | 2-4 词标题前缀 |
| `title.highlight` | 1-3 词高亮词（绿色胶囊背景） |
| `title.subtitle` | 副标题，一行 |
| `input_title` | 输入区标题 |
| `inputs[]` | 最多 4 个输入节点（icon + label） |
| `core.title` | 核心处理区标题 |
| `core.cards[]` | 3 张核心处理卡（icon + title + body，每个 body ≤2 行 ≤22 字符） |
| `decision` | 菱形决策节点（title + body） |
| `left_panel` | 左侧面板（来源/输入储存） |
| `center_panel` | 中间面板（内部层级，最多 4 列） |
| `right_panel` | 右侧面板（输出/打包） |

---

## [2] JSON Spec 结构

```json
{
  "title": {
    "prefix": "The internals of",
    "highlight": "Archer Router",
    "subtitle": "local-first LLM routing architecture"
  },
  "signature": "@archsueh",
  "input_title": "Request / Input",
  "inputs": [
    {"label": "Claude CLI", "icon": "file"},
    {"label": "Codex CLI",  "icon": "file"},
    {"label": "Hermes",     "icon": "folder"},
    {"label": "agy CLI",    "icon": "package"}
  ],
  "core": {
    "title": "LocalRouter Core",
    "subtitle": "(Python, ~200 lines)",
    "cards": [
      {"title": "Classifier",  "body": "Qwen3-4B\nintent scoring",  "icon": "scan",    "color": "#7ee3d6"},
      {"title": "Router",      "body": "threshold\ndispatch",        "icon": "shield",  "color": "#22c86f"},
      {"title": "Fallback",    "body": "Claude API\nfailover",       "icon": "db",      "color": "#bd54d3"}
    ]
  },
  "decision": {"title": "Simple?", "body": "< threshold\nlocal ok"},
  "output":   {"label": "Response", "icon": "package"},
  "loop_label":  "Retry with stronger model",
  "retry_label": "No / complex / tool-heavy",
  "left_panel": {
    "title": "Local Tier",
    "badge": "zero cost",
    "cards": [
      {"title": "Qwen3-4B",   "body": "mlx_lm.server\n~100ms",     "icon": "db",     "color": "#7ee3d6"},
      {"title": "FreeLLMAPI", "body": "16 free providers\nlocalhost:3000", "icon": "folder", "color": "#22c86f"},
      {"title": "Ollama",     "body": "fallback\nlocal",            "icon": "file",   "color": "#7ee3d6"}
    ]
  },
  "center_panel": {
    "title": "Routing Logic",
    "subtitle": "(intent classification + threshold)",
    "footer": "Protocol Bridge",
    "cards": [
      {"title": "Simple",   "body": "→ local",    "icon": "hash",    "color": "#7ee3d6"},
      {"title": "Medium",   "body": "→ free",     "icon": "hash",    "color": "#22c86f"},
      {"title": "Complex",  "body": "→ Claude",   "icon": "shield",  "color": "#bd54d3"},
      {"title": "Retrieval","body": "→ Grok/agy", "icon": "scan",    "color": "#f4b64e"}
    ]
  },
  "right_panel": {
    "title": "Cloud Tier",
    "incoming_label": "Dispatch",
    "return_label": "Result",
    "cards": [
      {"title": "Claude API", "body": "complex\nreasoning",  "icon": "shield",  "color": "#bd54d3"},
      {"title": "Grok Build", "body": "Twitter/X\ndata",     "icon": "scan",    "color": "#f4f0ee"},
      {"title": "agy CLI",    "body": "general\ntasks",      "icon": "package", "color": "#4285F4"}
    ]
  }
}
```

---

## [3] 渲染命令

```bash
# 安装依赖（一次）
pip install "Pillow>=10.0.0"

# 渲染
python3 ~/.agents/skills/archviz-animationd/scripts/render_animated_diagram.py \
  --spec spec.json \
  --outdir ./output \
  --basename archer-router \
  --verify \
  --check
```

输出：
- `output/archer-router.png`         — 静态预览（1210×1138）
- `output/archer-router.gif`         — 41 帧 20FPS 动画
- `output/archer-router.excalidraw`  — Excalidraw 可编辑源

---

## [4] 验证标准

| 检查项 | 期望值 |
|---|---|
| GIF 尺寸 | 1210 × 1138 |
| GIF 帧数 | 41 |
| GIF FPS | 20 |
| GIF 有动效 | 帧差 changed_pixels > 0 |
| Excalidraw ID 唯一 | ✅ |
| text fontFamily | 5（全部） |
| files 对象 | 空 {} |

`--check` 失败时 exit code 非零，可接入 CI。

---

## [5] 可用 Icon 列表

`folder` `file` `scan` `shield` `db` `hash` `package`

## [6] 柱状图动画 (Bar Chart Animation)

交叉优化：archviz-diagram + archviz-animation

**功能：** 将柱状图数据转换为生长动画 GIF

**脚本：** `scripts/render_animated_bar_chart.py`

**数据格式：**
```json
{
  "title": "Chart Title",
  "subtitle": "Description",
  "categories": ["A", "B", "C"],
  "values": [10, 20, 15],
  "labels": ["Label A", "Label B", "Label C"],
  "width": 800,
  "height": 500
}
```

**渲染命令：**
```bash
python3 scripts/render_animated_bar_chart.py \
  --spec data.json \
  --outdir ./output \
  --basename chart-name \
  --frames 30 \
  --fps 15
```

**参数：**
- `--frames`: 帧数（默认 30）
- `--fps`: 帧率（默认 15）

**输出：**
- `chart-name.gif` — 动画
- `chart-name.png` — 静态图

**动画效果：**
- 柱状图从底部生长
- ease-out 缓动函数
- 数值标签淡入

---

## [7] 数学可视化动画 (Math Visualization)

风格参考：3Blue1Brown / THEMATHFLOW

**功能：** 数学教育类可视化动画（三角函数、单位圆等）

**脚本：** `scripts/render_math_visualization.py`

**风格特点：**
- 极简主义 + 现代科技感
- 低饱和度柔和配色（暖橙、玫红、蓝青）
- 三维透视多平面构图
- 实时联动动态演示
- 数学符号支持

**数据格式：**
```json
{
  "title": "Unit Circle & Trigonometric Functions",
  "subtitle": "sin(x) and cos(x) visualization",
  "width": 1200,
  "height": 800
}
```

**渲染命令：**
```bash
python3 scripts/render_math_visualization.py \
  --spec math-spec.json \
  --outdir ./output \
  --basename math-viz \
  --frames 60 \
  --fps 30 \
  --theme color  # or mono
```

**主题选项：**
- `color` — 暖橙+玫红+蓝青（3Blue1Brown 风格）
- `mono` — 黑白极简风格

**输出：**
- `math-viz.gif` — 动画
- `math-viz.mp4` — 视频
- `math-viz.png` — 静态图

**动画效果：**
- 单位圆旋转
- sin/cos 曲线实时绘制
- 投影线联动
- 数值实时更新

**适用场景：**
- 数学教育视频
- 科学概念演示
- 数据可视化
- 教学课件

---

## [8] 物理场可视化 (Yang-Mills Gauge Field)

**功能：** 物理规范场可视化动画（杨-米尔斯理论）

**实现：**
- `output/yang-mills.html` — WebGL Three.js 自包含（推荐，实时渲染）
- `scripts/render_yang_mills.py` — Python matplotlib（离线渲染 MP4）

**风格特点：**
- 暗黑背景 + 发光场强表面
- Viridis 色系渐变（暗蓝→青绿→黄）
- 内部规范方向颜色映射
- 移动 Wilson 回路
- GPU 着色器实时计算曲率 F = dA + A∧A

**WebGL 版本打开：**
```bash
open examples/yang-mills.html
```

**Python 版本渲染：**
```bash
PYTHONPATH="" /usr/bin/python3 scripts/render_yang_mills.py \
  --out output/yang-mills.mp4 \
  --frames 180 \
  --fps 30 \
  --strength 1.8 \
  --coupling 0.6
```

**参数：**
- `--strength`：规范场振幅（默认 1.8）
- `--coupling`：自相互作用强度（默认 0.6）
- `--frames`：帧数（默认 180）
- `--fps`：帧率（默认 30）

**适用场景：**
- 物理教育视频
- 科学可视化
- 理论物理演示

---

- `title.prefix`：2-4 词
- `title.highlight`：1-3 词
- 每张 card 的 `body`：≤2 行，每行 ≤22 字符（渲染器会自动缩小字体作为安全网，但超限会影响美观）
- CJK 字符支持，自动换行
