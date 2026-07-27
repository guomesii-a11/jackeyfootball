---
name: dark-theme-and-radar-colors
overview: 将前端整体主题调整为"更偏黑的深色背景 + 白色字体"，并将雷达图各球员数据系列改为多彩调色板（橙/青/绿/紫/黄/粉），在黑底上鲜明区分。
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
    fontFamily: PingFang SC
    heading:
      size: 48px
      weight: 800
    subheading:
      size: 32px
      weight: 600
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
  - id: update-theme-tokens
    content: 修改 style.css 与 tailwind.config.js 背景压黑、文字纯白
    status: completed
  - id: radar-multicolor
    content: 改造 RadarCompare.vue 注入多彩调色板并提升可读性
    status: completed
    dependencies:
      - update-theme-tokens
  - id: visual-verify
    content: 启动前端视觉验证背景偏黑、文字白、雷达多彩区分
    status: completed
    dependencies:
      - radar-multicolor
---

## 用户需求

将网站整体视觉主题调整为「黑色背景 + 白色字体」效果，但保留当前深色基调、仅向黑色方向进一步压暗（非纯黑死板）；同时将雷达图中不同球员的数据系列（线条/填充）改为在黑底上鲜明区分的多彩调色板。

## 产品概述

在不改动页面结构与布局的前提下，统一更新全局色彩令牌：背景由深蓝渐变压暗为接近黑的深灰黑渐变，文字统一提亮为纯白/浅白；雷达图各球员线条采用一组高对比彩色，便于多人对比时一眼区分。

## 核心特性

- 全局背景压暗：CSS 变量与 Tailwind 令牌的 bg0/bg1/bg2 调为接近黑的深灰黑，body 渐变同步更新。
- 字体统一白色：--text-0 调为纯白 #FFFFFF，--text-1 提亮；Tailwind 的 ink/muted 同步，所有页面文字随变量自动生效。
- 雷达图多彩配色：在 ECharts option 顶层注入多彩调色板，按球员顺序分配色彩，并适度加粗线条、提升填充不透明度，保证黑底可读性。

## 技术栈选择

- 前端框架：Vue 3 + Vite + TypeScript（现有项目，保持不变）
- 样式方案：Tailwind CSS（自定义颜色令牌）+ 全局 `style.css`（CSS 变量）
- 图表库：ECharts（`vue-echarts` 封装，RadarCompare.vue 已使用）

## 实现方案

### 策略

采用「集中令牌驱动」方式：所有页面颜色均通过 `style.css` 的 `:root` CSS 变量与 `tailwind.config.js` 的颜色 token 派生，因此只需改这两处令牌即可让全站背景更黑、文字更白；雷达图配色则在组件内显式声明 `option.color` 调色板，不污染全局令牌。

### 关键技术决策

1. **背景压暗但保留层次**：将 `--bg-0/1/2` 由 `#0b1020/#141b2e/#1c2540` 调整为接近黑的深灰黑（如 `#050608/#0A0C12/#11141C`），body 三段渐变同步改为同色系更黑版本，保留原有径向光晕营造的层次感，避免纯黑死板。
2. **文字纯白化**：`--text-0` 调为 `#FFFFFF`，`--text-1` 由 `#aeb8cc` 提亮到 `#C7CEDB`；Tailwind 的 `ink`/`muted` 与之一致，nav-link、SideNav、各 view 的 `text-ink`/`text-muted` 无需逐个改动即可生效。
3. **雷达图多彩调色板**：在 `option` 顶层加 `color: [...]`（橙/青/绿/紫/金/粉六色），ECharts 会按球员顺序自动分配；同时把 `legend.textStyle.color`、`radar.axisName.color` 改为浅白，网格线保持低透明度白，系列 `lineStyle.width` 提至 2、`areaStyle.opacity` 提至约 0.2，确保黑底对比清晰。

### 性能与可靠性

- 仅修改静态样式与一处图表配置，无运行时开销变化；CSS 变量与 Tailwind 令牌均在前端构建期解析，无额外渲染成本。
- 改动范围收敛于 3 个文件，不涉及路由/接口/数据结构，回归风险极低。

## 实现要点（执行细节）

- 保持 `App.vue` 中 `.bg-glow` 橙/青/紫光晕不变（更黑背景下更突出，可酌情将 opacity 从 0.32 略降到 0.28 以免过曝，非必须）。
- 雷达调色板顺序需覆盖默认全体对比上限（6 人），六色足够；若超 6 人 ECharts 会循环取色，可接受。
- 修改 `tailwind.config.js` 后需确认 `bg0/bg1/bg2/ink/muted` 与 `style.css` 数值一致，避免双源不一致。

## 目录结构（受影响文件）

```
frontend/
├── src/
│   └── style.css              # [MODIFY] 调整 :root 的 --bg-0/1/2、--text-0/1，并重写 body 背景渐变更为接近黑的深灰黑
│   └── components/
│       └── RadarCompare.vue   # [MODIFY] 在 option 顶层注入多彩调色板；调亮 legend/axisName、加粗线条、提升填充不透明度
└── tailwind.config.js         # [MODIFY] 同步 colors 中的 bg0/bg1/bg2（更黑）、ink（纯白 #FFFFFF）、muted（提亮）
```

## 关键代码结构（调色板示意）

```ts
// RadarCompare.vue — option 顶层
const PALETTE = ['#FF5A36', '#1FB6C9', '#2ECC71', '#9B59F6', '#FFC53D', '#FF7AB6']
const option = computed(() => ({
  color: PALETTE,
  legend: { textStyle: { color: '#E8ECF2' }, top: 0 },
  radar: {
    axisName: { color: '#FFFFFF' },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,.12)' } },
    splitArea: { areaStyle: { color: ['rgba(255,255,255,.03)', 'rgba(255,255,255,.06)'] } },
    axisLine: { lineStyle: { color: 'rgba(255,255,255,.15)' } },
  },
  series: [{
    type: 'radar',
    data: props.players.map((p) => ({
      name: p.name,
      value: dims.map((d) => p.score_breakdown?.[d] ?? 0),
      lineStyle: { width: 2 },
      areaStyle: { opacity: 0.2 },
    })),
  }],
}))
```

## 设计风格

在保持现有页面结构与玻璃拟态卡片布局不变的前提下，将整体视觉基调由深蓝渐变压暗为接近黑的深灰黑渐变，文字统一为纯白/浅白，营造冷峻、高对比、科技感更强的暗色主题。雷达图切换为多彩高亮数据系列，在黑底上形成鲜明区分。

## 页面与区块说明

- 全局背景：三段式深灰黑渐变（左上/右下径向光晕保留），整体明显偏黑但留有层次。
- 顶部导航与侧边导航：文字由近白提亮为纯白，激活态半透明白底不变，玻璃卡片边框保留。
- 雷达图区块：网格线与轴名为浅白，各球员多边形按多彩调色板着色，线条加粗、填充微提透明度，多人对比一目了然。