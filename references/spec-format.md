# Spec Format 参考

`render_animated_diagram.py` 接受的 JSON spec 完整字段说明。

## 顶层字段

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `title.prefix` | string | "The internals of" | 标题前缀，2-4 词 |
| `title.highlight` | string | "Memory Pack" | 高亮词，绿色胶囊，1-3 词 |
| `title.subtitle` | string | "" | 副标题，灰色小字 |
| `signature` | string | "@archsueh" | 右上角签名 |
| `input_title` | string | "Source / Input" | 输入区标题 |
| `inputs` | array[4] | — | 输入节点，每个含 `icon` + `label` |
| `decision.title` | string | "Ready?" | 菱形决策节点标题 |
| `decision.body` | string | — | 菱形决策节点副文本 |
| `output.icon` | string | "file" | 输出节点 icon |
| `output.label` | string | "Report" | 输出节点标签 |
| `loop_label` | string | — | 回环虚线上方文字 |
| `retry_label` | string | — | 回环虚线下方文字 |
| `canvas.width` | int | 1210 | 画布宽度（px） |
| `canvas.height` | int | 1138 | 画布高度（px） |
| `canvas.frames` | int | 41 | GIF 总帧数 |
| `canvas.fps` | int | 20 | GIF 帧率 |

## core（核心处理区）

```json
"core": {
  "title": "Core Name",
  "subtitle": "(description)",
  "cards": [
    {"title": "Card 1", "body": "line1\nline2", "icon": "scan", "color": "#7ee3d6"},
    {"title": "Card 2", "body": "line1\nline2", "icon": "shield"},
    {"title": "Card 3", "body": "line1\nline2", "icon": "db"}
  ]
}
```

- 固定 3 张 card，从左到右排列
- `body` 每行 ≤22 字符，最多 2 行

## left_panel（左侧面板）

```json
"left_panel": {
  "title": "Panel Title",
  "badge": "badge text",
  "cards": [
    {"title": "Item 1", "body": "desc\nline2", "icon": "db",     "color": "#7ee3d6"},
    {"title": "Item 2", "body": "desc\nline2", "icon": "folder"},
    {"title": "Item 3", "body": "desc",        "icon": "file"}
  ]
}
```

- 最多 3 张 mini_card（绿色边框）
- 第 3 张高度略小（62px vs 78px）

## center_panel（中间面板）

```json
"center_panel": {
  "title": "Panel Title",
  "subtitle": "(description)",
  "footer": "Footer Text",
  "cards": [
    {"title": "Col 1", "body": "desc", "icon": "hash",    "color": "#7ee3d6"},
    {"title": "Col 2", "body": "desc", "icon": "hash"},
    {"title": "Col 3", "body": "desc", "icon": "shield"},
    {"title": "Col 4", "body": "desc", "icon": "scan"}
  ]
}
```

- 最多 4 列竖向卡（紫色边框）
- `footer` 显示在中间面板底部

## right_panel（右侧面板）

```json
"right_panel": {
  "title": "Panel Title",
  "incoming_label": "Compile",
  "return_label": "Reusable",
  "cards": [
    {"title": "Row 1", "body": "desc\nline2", "icon": "shield", "color": "#bd54d3"},
    {"title": "Row 2", "body": "desc\nline2", "icon": "scan"},
    {"title": "Row 3", "body": "desc\nline2", "icon": "package"}
  ]
}
```

- 最多 3 行 pack_row（绿色边框）

## 可用 Icon

| key | 外形 |
|---|---|
| `folder` | 文件夹 |
| `file` | 文件（带横线） |
| `scan` | 放大镜 |
| `shield` | 盾牌（带勾） |
| `db` | 圆柱数据库 |
| `hash` | # 符号 |
| `package` | 六边形包裹 |

## 颜色参考（THEME）

| 名称 | HEX | 用途 |
|---|---|---|
| cyan | `#7ee3d6` | 默认 icon 色 |
| green | `#22c86f` | 主强调色 |
| purple | `#bd54d3` | 次强调色 |
| amber | `#f4b64e` | hash icon / 箭头 |
| white | `#f4f0ee` | 主文字 |
| muted | `#cfc7c5` | 副文字 |
