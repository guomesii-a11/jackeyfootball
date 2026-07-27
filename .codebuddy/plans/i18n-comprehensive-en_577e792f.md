---
name: i18n-comprehensive-en
overview: 将所有页面硬编码中文字符串改为 i18n 翻译调用，包括侧边栏副标题、数据排名页标题/副标题、对比页雷达图维度标签和图例球员名
todos:
  - id: i18n-sidenav
    content: 修改 SideNav.vue：cards 数组 desc 改为 descKey 并指向 i18n 键，模板使用 t() 渲染
    status: completed
  - id: i18n-data-ranking
    content: 修改 DataRankingView.vue：标题与副标题改为 t() 调用，去除硬编码中文
    status: completed
  - id: i18n-radar-compare
    content: 修改 RadarCompare.vue：注入 useI18n，删除 DIM_LABELS，维度与球员名随 locale 切换
    status: completed
  - id: verify-en-display
    content: 在 EN 语言下验证三处页面文案与雷达图球员名均为英文
    status: completed
    dependencies:
      - i18n-sidenav
      - i18n-data-ranking
      - i18n-radar-compare
---

## 产品概述

在语言切换到 EN 时，将页面中所有仍显示中文硬编码字符串的位置改造为 i18n 翻译调用，确保界面文案（中英文混合显示问题）随语言切换同步更新。涉及侧边栏副标题、数据排名页标题/副标题、对比页雷达图的维度标签与球员名称。

## 核心特性

- 左侧引导栏 Power / Stats / Compare 三张卡片的副标题在 EN 下显示英文
- 数据排名页（/data）H1 标题与下方副标题段落在 EN 下显示英文
- 对比页（/compare）雷达图的六个维度标签（团队荣誉 / 团队实力 / 个人荣誉 / 个人数据 / 队长影响力 / 身价）在 EN 下显示英文
- 对比页雷达图的图例与系列名（球员名）在 EN 下显示英文（哈里·凯恩 → Harry Kane 等）
- 中文语言下保持现有显示效果不变

## 边界与输入输出

- 输入：用户在顶栏切换 `localStorage.jf_lang` 为 `en`
- 输出：上述三处位置文案与球员名随 `locale.value` 反应式更新
- 不修改 i18n 词条文件本身，仅消费已有键值

## 技术栈

- Vue 3 `<script setup lang="ts">`
- vue-i18n（已通过 `useI18n()` 在涉及的组件中注入）
- ECharts via vue-echarts（用于雷达图维度标签与系列名）
- 复用现有 i18n 键值：`sideNav.powerDesc/dataDesc/compareDesc`、`data.title/subtitle`、`bd.honor_raw/award_raw/stats_raw/market_value_raw/leadership_raw/team_strength_raw`

## 实施方案

### 1. 改造策略

将硬编码中文字符串统一替换为 `t()` 调用，与现有 `titleKey` 模式对齐；雷达图维度标签与球员名按 `locale` 选择中英文显示。无需新增任何 i18n 键值（`zh` 与 `en` 两套文案已完整覆盖），不影响中文显示。

### 2. 修改点

**A. `frontend/src/components/SideNav.vue`**

- `cards` 数组（第 8-10 行）：`desc: '中文'` → `descKey: 'sideNav.xxxDesc'`（与 `titleKey` 命名一致）
- 模板（第 31 行）：`{{ c.desc }}` → `{{ t(c.descKey) }}`

**B. `frontend/src/views/DataRankingView.vue`**

- 第 85 行 `<h1>各数据排名</h1>` → `<h1>{{ t('data.title') }}</h1>`
- 第 86 行 `<p>全部球员按所选指标统一排名对比。</p>` → `<p>{{ t('data.subtitle') }}</p>`

**C. `frontend/src/components/RadarCompare.vue`**（核心新增）

- `import { useI18n }` 并在 setup 中获取 `t` 与 `locale`
- 删除硬编码 `DIM_LABELS` 常量（第 14-21 行）
- `option` 计算属性中：
- `indicator` 维度标签：`{ name: DIM_LABELS[d] || d, max: 100 }` → `{ name: t('bd.' + d), max: 100 }`（`bd.*` 键已存在，缺失键会回退 key 名）
- `legend.data`：`props.players.map(p => p.name)` → 根据 `locale` 选择 `p.name_en || p.name`
- `series.data[].name`：同上选择策略
- 球员名切换函数：`nameOf(p)` 复用 `CompareView.vue` 中的模式（`locale === 'en' ? p.name_en || p.name : p.name`）

### 3. 实施步骤

1. 修改 `SideNav.vue`：将 `desc` 改为 `descKey`，模板用 `t(c.descKey)` 渲染
2. 修改 `DataRankingView.vue`：标题与副标题改为 `t()` 调用
3. 修改 `RadarCompare.vue`：注入 `useI18n`，删除 `DIM_LABELS`，在 `option` 计算中使用 `t('bd.' + d)` 与 `nameOf()`
4. 验证：EN 下三处均显示英文；中文下显示无变化

## 实施细节（防回归）

- **模式对齐**：SideNav 的 `descKey` 与已有 `titleKey` 命名风格一致；`nameOf` 模式与 `CompareView.vue:34-36` 一致
- **i18n 完备性**：`zh` 与 `en` 下的 `sideNav.*`、`data.title/subtitle`、`bd.*` 键值均已存在，无需修改 `frontend/src/i18n/index.ts`
- **反应式**：`t()` 与 `locale` 均为响应式，切换语言后文案即时更新；ECharts 通过 `computed` 重新计算 `option`，vue-echarts 自动重绘
- **缺失键保护**：维度键若未命中 `bd.*` 的 i18n 表，会回退为原 key 名（不会报错），但当前 `score_breakdown` 的 6 个维度键已全部覆盖
- **球员名回退**：`name_en || name` 保证缺失英文名时回退中文，避免空白图例
- **影响范围**：仅 3 个文件，14 处字符改动；不新增/删除文件，不修改依赖与配置

## 目录结构

```
frontend/src/
├── components/
│   ├── SideNav.vue          # [MODIFY] cards 数组 + 模板
│   └── RadarCompare.vue     # [MODIFY] 引入 useI18n，删除 DIM_LABELS，option 计算改造
└── views/
    └── DataRankingView.vue  # [MODIFY] header 标题/副标题
```

## 关键类型（已存在，无需新增）

- `PlayerDetail extends PlayerListItem`：包含 `name`、`name_en`、`score_breakdown: Record<string, number> | null`
- `score_breakdown` 包含键：`honor_raw`、`award_raw`、`stats_raw`、`market_value_raw`、`leadership_raw`、`team_strength_raw`、`age_raw`（radar 已过滤掉 `age_raw`）