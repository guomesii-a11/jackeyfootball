---
name: radar-black-bg-and-header-white
overview: 将雷达图内部区域背景改为黑色（当前在黑底页面下仍呈现白/亮色），并把"各数据排名"页标题与副标题改为白色、字体调大。
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
    fontFamily: "\"Times New Roman\", Times, serif"
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
  - id: radar-bg-black
    content: 改造 RadarCompare.vue 雷达内圈背景为纯黑并降低数据填充不透明度
    status: completed
  - id: data-header-style
    content: 将 DataRankingView.vue 顶部标题与副标题改为白色并调大字号
    status: completed
  - id: visual-verify
    content: 启动前端视觉验证雷达黑底白字、各数据页标题白字大号
    status: completed
    dependencies:
      - radar-bg-black
      - data-header-style
---

## 产品概述

针对上一轮主题调整的两点修正：

1. 雷达图内部区域背景由"泛白"改为纯黑（保留多彩球员多边形与白色轴名/legend），多人对比时多边形重叠不会洗白。
2. /data 页顶部"各数据排名"标题与"全部球员按所选指标统一排名对比"副标题统一为白色，并整体调大字号，配合全局黑色背景可读。

## 核心特性

- 雷达 inner area 设纯黑：显式 `backgroundColor: '#000000'` + `splitArea.show: false`，并把球员多边形 `areaStyle.opacity` 由 0.2 降至 0.12 避免重叠洗白；轴名/legend 保持白色。
- DataRankingView 顶部 header：h1 改为 `text-4xl font-extrabold text-white`；副标题改为 `text-base text-white/80`，与全局深色主题匹配。

## 技术栈

保持现有 Vue 3 + Vite + TypeScript + Tailwind + ECharts（vue-echarts）技术栈不变，仅做样式/图表 option 微调，Vite HMR 即时生效。

## 影响文件

- `frontend/src/components/RadarCompare.vue`（修改图表 option）
- `frontend/src/views/DataRankingView.vue`（仅修改顶部 header）

## 实现要点

### RadarCompare.vue option 调整

```ts
radar: {
  backgroundColor: '#000000',                  // 雷达区显式纯黑
  splitArea: { show: false },                  // 关掉交替浅色填充，去掉泛白
  splitLine: { lineStyle: { color: 'rgba(255,255,255,.18)' } },
  axisLine:  { lineStyle: { color: 'rgba(255,255,255,.25)' } },
  axisName:  { color: '#FFFFFF' },
}
series: [{
  type: 'radar',
  data: props.players.map(p => ({
    name: p.name,
    value: dims.map(d => p.score_breakdown?.[d] ?? 0),
    lineStyle: { width: 2 },
    areaStyle: { opacity: 0.12 },              // 0.2 -> 0.12 防洗白
  })),
}]
```

仍保留 `color: PALETTE`、`legend.textStyle.color: '#E8ECF2'`。

### DataRankingView.vue header 改为

```html
<header class="mb-8">
  <h1 class="text-4xl font-extrabold text-white">各数据排名</h1>
  <p class="mt-2 text-base text-white/80">全部球员按所选指标统一排名对比。</p>
</header>
```

（本轮用户只要求顶部 header 调整，其余页面其它 `text-slate-*` 不动。）

## 性能与可靠性

- 仅样式/图表 option 改写，无新依赖、无网络调用；echarts option 变更触发局部重绘，对其它区块零影响。
- `splitArea.show:false` 减少 echarts 渲染分块，略微降低 CPU 开销。