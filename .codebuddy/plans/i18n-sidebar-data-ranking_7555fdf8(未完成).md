---
name: i18n-sidebar-data-ranking
overview: 将左侧引导栏副标题和右侧数据排名页面的硬编码中文字符串改为 i18n 翻译调用，使其在英文环境下正确显示英文
todos:
  - id: update-sidenav-desckey
    content: 将 SideNav.vue 的 cards 数组 desc 字段改为 descKey 并指向 i18n 键]
    status: pending
---

## 用户需求

当前页面顶部语言切换器选择 EN 时，左侧引导栏副标题（Power/Stats/Compare 卡片下方的中文描述）以及右侧数据排名页面的标题与副标题仍显示中文硬编码字符串，无法跟随语言切换。

**需要修改的位置：**

1. 左侧引导栏 Power 卡片副标题：`全部球员综合实力排名` → 英文
2. 左侧引导栏 Stats 卡片副标题：`进球 / 助攻 / 传球逐项排名` → 英文
3. 左侧引导栏 Compare 卡片副标题：`全体 / 跨位置雷达图对比` → 英文
4. 右侧页面 H1 标题：`各数据排名` → 英文
5. 右侧页面副标题段落：`全部球员按所选指标统一排名对比。` → 英文

## 产品概述

将上述硬编码中文字符串改为调用 `vue-i18n` 的 `t()` 翻译函数，切换语言时文案自动随语言变化。所需中英文翻译键值已存在于 `frontend/src/i18n/index.ts`，无需新增。

## 核心特性

- 侧边栏 3 张卡片的副标题在 EN 语言下显示对应英文文案
- 数据排名页（/data）标题与副标题在 EN 语言下显示对应英文文案
- 不改动 i18n 配置、不影响其他页面与中文显示效果

## 技术栈

- Vue 3 + `<script setup lang="ts">`
- vue-i18n（已通过 `useI18n()` 在两个文件中注入）
- 复用现有 i18n 键值：`sideNav.powerDesc` / `sideNav.dataDesc` / `sideNav.compareDesc`、`data.title` / `data.subtitle`

## 实施方案

将硬编码中文文案替换为 i18n 键引用，保持与现有 `titleKey` 模式一致：

1. **`frontend/src/components/SideNav.vue`**

- `cards` 数组（第 8-10 行）`desc: '中文'` → `descKey: 'sideNav.xxxDesc'`
- 模板（第 31 行）`{{ c.desc }}` → `{{ t(c.descKey) }}`

2. **`frontend/src/views/DataRankingView.vue`**

- 第 85 行 `<h1>各数据排名</h1>` → `<h1>{{ t('data.title') }}</h1>`
- 第 86 行 `<p>全部球员按所选指标统一排名对比。</p>` → `<p>{{ t('data.subtitle') }}</p>`

## 实施细节（防回归）

- 模式对齐：复用现有 `titleKey` 的命名与模板用法（参见 `SideNav.vue:30`），不引入新的属性命名风格
- i18n 已具备：`zh` 与 `en` 下的 `sideNav.*` 与 `data.title/subtitle` 键值均已存在，无需修改 `frontend/src/i18n/index.ts`
- 反应式：使用 `t()`（而非静态字符串），确保 `localStorage` 中 `jf_lang` 切换后文案立即更新
- 影响范围最小：仅修改 2 个文件的 4 处字符串，风险局限于侧边栏与 `/data` 路由的标题展示

## 架构设计

遵循现有分层架构（视图组件 → i18n 消息映射），无新架构或新依赖。

## 目录结构

仅修改文件，无新增/删除：

```
frontend/src/
├── components/
│   └── SideNav.vue          # [MODIFY] cards 数组 + 模板
└── views/
    └── DataRankingView.vue  # [MODIFY] header 标题/副标题
```