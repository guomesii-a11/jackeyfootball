---
name: compare-remove-pos-chips-and-label
overview: 去掉 CompareView 搜索框上方的位置筛选 chips，并把候选球员按钮改为中文名（英文模式下显示英文名），名字前加"热门球员："前缀。
todos:
  - id: simplify-compare
    content: 修改 CompareView.vue：移除位置筛选 chips、清理相关状态、名字本地化并添加"热门球员："前缀
    status: completed
  - id: preview-verify
    content: 预览 /compare 确认 chips 已移除、候选名字为中文且带前缀
    status: completed
    dependencies:
      - simplify-compare
---

## 用户需求

1. 去掉球员对比页（/compare）搜索框上方的位置筛选 chips："全部 / 前锋 / 中场 / 后卫 / 门将"。
2. 搜索框下方候选球员按钮的名字改为中文名（英文 locale 下显示英文名），并在前面统一加上"热门球员："前缀。
3. 已选球员标签中的名字也同步按当前语言环境显示。

## 产品概述

精简球员对比页的交互：移除位置筛选，仅保留搜索+自选模式；候选列表按当前语言展示球员名，并统一冠以"热门球员："引导标签。

## 核心特性

- 移除位置筛选 chips 及相关状态（posFilter、POS_OPTIONS、defaultPlayers）。
- 候选球员名字本地化：zh 显示 `p.name`，en 显示 `p.name_en || p.name`。
- 已选标签名字同步本地化。
- 在候选按钮列表前添加"热门球员："前缀。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Tailwind CSS + vue-i18n
- 图表：ECharts（vue-echarts），本轮不涉及

## 实现方案

采用与 `PowerRankingView.vue` 一致的 `useI18n().locale` 模式实现中英文切换。删除 CompareView 中不再使用的位置筛选相关代码，使 `available` 直接搜索全部球员。候选列表与已选标签统一使用 `nameOf(p)` 计算显示名。

## 关键代码结构

```ts
// CompareView.vue
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()

function nameOf(p: PlayerDetail) {
  return locale.value === 'zh' ? p.name : p.name_en || p.name
}
```

```html
<!-- 候选列表 -->
<div v-if="available.length" class="mb-3">
  <div class="mb-2 text-sm font-medium text-black/70">热门球员：</div>
  <div class="flex flex-wrap gap-2">
    <button v-for="p in available" ...>
      {{ nameOf(p) }}
    </button>
  </div>
</div>
```

## 目录结构

```
frontend/
└── src/
    └── views/
        └── CompareView.vue       # [MODIFY] 移除位置筛选 chips、名字本地化、添加"热门球员："前缀
```