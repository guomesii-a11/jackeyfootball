---
name: compare-view-radar-refresh
overview: 改造 CompareView 与 RadarCompare：标题白字大号、雷达图 legend/轴名改黑色、删掉"巅峰年龄"维度、初始不显示雷达图改为空白待选（最多4人）。
design:
  architecture:
    framework: vue
  styleKeywords:
    - Dark Theme
    - Near-Black Background
    - White Text
    - High Contrast
    - Multicolor Radar
    - Glassmorphism
  fontSystem:
    fontFamily: Georgia, serif
    heading:
      size: 48px
      weight: 900
    subheading:
      size: 32px
      weight: 700
    body:
      size: 16px
      weight: 500
  colorSystem:
    primary:
      - "#FF5A36"
      - "#1FB6C9"
      - "#2ECC71"
      - "#9B59F6"
      - "#FFC53D"
      - "#FF7AB6"
    background:
      - "#050608"
      - "#0A0C12"
      - "#11141C"
    text:
      - "#FFFFFF"
      - "#C7CEDB"
    functional:
      - "#E8ECF2"
      - "#FF5A36"
todos:
  - id: compare-view-header-and-empty
    content: 修改 CompareView.vue：标题白字大号、空状态提示、4人上限、移除恢复全部按钮
    status: completed
  - id: radar-labels-and-colors
    content: 修改 RadarCompare.vue：因素标签、过滤age_raw、legend与轴名黑色、网格线深色
    status: completed
  - id: visual-verify
    content: 预览验证：标题白字、雷达空状态、4人黑字雷达、6因素
    status: completed
    dependencies:
      - compare-view-header-and-empty
      - radar-labels-and-colors
---

## 产品概述

针对“球员对比 · 综合数据”页（/compare）的样式与交互修正：

1. 页面标题“球员对比 · 综合数据”改为白色、字号调大（text-4xl font-extrabold）。
2. 雷达图上方 legend（球员名字）字体改为黑色。
3. 雷达图轴名（对比因素）字体改为黑色。
4. 雷达图因素标签调整：“身价年龄”改为“身价”；移除“巅峰年龄”，仅保留 6 个因素。
5. 雷达图初始状态为空白，不默认展示任何球员；用户通过搜索勾选后才显示，最多支持 4 人对比。

## 核心特性

- **标题白色大号**：CompareView 顶部 h1/p 改为白色系，字号提升。
- **雷达图黑底黑字**：legend 与 axisName 设为 `#000000`，网格线改用深灰色（`rgba(0,0,0,…)`）以在白色卡片背景上可见；雷达内圈保持纯黑。
- **6 因素雷达**：DIM_LABELS 中 `market_value_raw` 标签改为“身价”，`age_raw` 移除；组件内显式过滤掉 `age_raw`，确保 `Object.keys(score_breakdown)` 不将其纳入 indicator。
- **空状态 + 4 人上限**：CompareView 初始 `radarPlayers` 为空，展示提示文案；`customIds` 上限由 6 改为 4；搜索占位符同步更新；位置筛选 chips 仅用于过滤候选列表，不直接触发雷达图渲染。

## 边界与范围

- 仅修改前端 CompareView.vue 与 RadarCompare.vue，不改动后端 scoring 逻辑（后端仍返回 7 字段，前端过滤展示）。
- DataRankingView 等其他页面不受影响。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Tailwind CSS + ECharts（vue-echarts）
- 无需新增依赖

## 实现方案

### 策略

采用“前端过滤 + 令牌微调”策略：后端 `score_breakdown` 保持 7 字段不变，RadarCompare 通过显式排除 `age_raw` 实现 6 因素雷达；CompareView 通过条件渲染控制空状态与 4 人上限。

### 关键技术决策

1. **不改动后端**：`scoring.py` 的 `_build_breakdowns` 仍返回 `age_raw`，避免影响数据排名等其他页面。RadarCompare 在 `computed` 里用 `Object.keys(...).filter(k => k !== 'age_raw')` 过滤，保证向后兼容。
2. **legend / axisName 黑色**：外层卡片为 `bg-white`，黑色文字在白色卡片上可读；雷达内圈 `backgroundColor: '#000000'` 保留，形成“黑底雷达 + 白底卡片 + 黑字标注”的层次。
3. **空状态交互**：`radarPlayers` 改为仅当 `customIds.length > 0` 时返回勾选球员，否则空数组；配合条件渲染展示占位提示，引导用户搜索勾选。

## 实现要点（执行细节）

- CompareView 中 `radarPlayers` computed 逻辑调整：

```ts
const radarPlayers = computed(() =>
customIds.value.length > 0
? customIds.value.map(id => allPlayers.value.find(p => p.id === id)).filter(Boolean) as Player[]
: []
)
```

- 勾选上限提示文本、搜索框 placeholder 统一替换为“最多 4 人”。
- RadarCompare 中 `splitLine` / `axisLine` 颜色由白色半透明改为黑色半透明（如 `rgba(0,0,0,.15)`），确保在白色卡片上可见。
- 调色板 `PALETTE` 保持 6 色，前 4 色已足够覆盖 4 人上限。

## 目录结构（受影响文件）

```
frontend/
├── src/
│   ├── views/
│   │   └── CompareView.vue       # [MODIFY] 标题白字大号、空状态、4人上限、移除恢复全部
│   └── components/
│       └── RadarCompare.vue      # [MODIFY] 因素标签、过滤age_raw、legend/轴名黑色、网格线深色
```

## 关键代码结构

```ts
// RadarCompare.vue — 过滤与标签
const DIM_LABELS: Record<string, string> = {
  honor_raw: '团队荣誉',
  award_raw: '个人荣誉',
  stats_raw: '个人数据',
  market_value_raw: '身价',
  leadership_raw: '队长影响力',
  team_strength_raw: '团队实力',
}

const option = computed(() => {
  const rawDims = Object.keys(props.players[0]?.score_breakdown ?? {})
  const dims = rawDims.filter(d => d !== 'age_raw')
  const indicator = dims.map((d) => ({ name: DIM_LABELS[d] || d, max: 100 }))
  return {
    color: PALETTE,
    legend: { textStyle: { color: '#000000' }, top: 0 },
    radar: {
      backgroundColor: '#000000',
      indicator, radius: '62%',
      axisName: { color: '#000000' },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,.15)' } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(0,0,0,.2)' } },
    },
    series: [{
      type: 'radar',
      data: props.players.map(p => ({
        name: p.name,
        value: dims.map(d => p.score_breakdown?.[d] ?? 0),
        lineStyle: { width: 2 },
        areaStyle: { opacity: 0.12 },
      })),
    }],
  }
})
```