---
name: homepage-redesign
overview: 重设计主页：移除顶部四个 nav 链接（logo 可点回主页），左侧三张导航卡片变大，右侧 hero 标题改为 80px 浅蓝渐变"JackeyFootball为你展现出最完整的球员数据"，去除下方白字。
todos:
  - id: update-app-nav
    content: 移除 App.vue 顶部 nav 链接、把 logo 包成 RouterLink 指向 /
    status: completed
  - id: enlarge-sidenav-cards
    content: 加大 SideNav.vue 三张引导卡片（padding/icon/字号）
    status: completed
  - id: hero-redesign
    content: HomeView.vue hero 改为 80px 浅蓝渐变大字、删除副标题
    status: completed
  - id: i18n-hero-copy
    content: 同步 i18n 文案（中/英 hero.title），英文也包含 JackeyFootball
    status: completed
    dependencies:
      - hero-redesign
  - id: preview-verify
    content: 预览首页确认导航精简、卡片放大、hero 80px 浅蓝渐变
    status: completed
    dependencies:
      - update-app-nav
      - enlarge-sidenav-cards
      - hero-redesign
      - i18n-hero-copy
---

## 产品概述

重设计主页（/）：

1. 顶部导航移除"首页/综合实力/各数据/球员对比"四个 nav 链接，把"JackeyFootball"logo 包成可点击的 RouterLink，点击回主页。
2. 主页左侧 35% 引导栏保留，三张引导卡片加大。
3. 右侧主区域显示 80px 的"JackeyFootball为你展现出最完整的球员数据"浅蓝渐变大字 hero，移除下方小的白色副标题。

## 核心特性

- 顶部导航精简为 logo + 语言切换，logo 整块点击回到 `/`。
- 左侧 SideNav 卡片加大（更大 padding、icon、字号）。
- 主页 hero 采用 80px 浅蓝渐变（from-sky-300 via-sky-400 to-cyan-300）粗体居中文案，中英文同步通过 i18n 切换。

## 技术栈

保持现有 Vue 3 + Vite + TypeScript + Tailwind CSS，仅样式/文案微调，Vite HMR 即时生效。

## 实现方案

### 1. App.vue 顶部导航改造

- 把 logo 整块用 `<RouterLink to="/" class="...">` 包裹，移除原 `<nav>` 中 4 个 nav-link（含 `.nav-link`/`.active` 相关 scoped style）。
- 保留 LangSwitch；保留背景光晕不变。

### 2. SideNav.vue 卡片加大

- RouterLink 容器：`p-5` → `p-7`、`gap-4` → `gap-5`，圆角、边框、hover 行为保留。
- icon 容器：`w-12 h-12` → `w-16 h-16`，图标 size `24` → `28`。
- 标题：`text-lg` → `text-2xl`，副标题：`text-sm` → `text-base`，在深色背景下保持可读。
- 外层 `<aside>` 的 `gap-4` 改为 `gap-6` 让卡片之间更有呼吸感。

### 3. HomeView.vue hero 重做

- 删除原 `<p class="mt-3 text-muted">`，只保留 h1。
- h1 改为 `text-[80px] leading-[1.05] font-extrabold bg-gradient-to-r from-sky-300 via-sky-400 to-cyan-300 bg-clip-text text-transparent` 居中显示，配合 `py-24` 上下留白。
- 文案通过 i18n 切换：zh `hero.title = 'JackeyFootball为你展现出最完整的球员数据'`；en `hero.title = 'JackeyFootball reveals the most complete player data for you'`。

### 4. i18n 文本同步

- 修改 `frontend/src/i18n/index.ts` 中 `messages.zh.hero.title` 与 `messages.en.hero.title`。
- 移除 `hero.sub`（如不再使用；保留键可避免 TS 报错）。

## 性能与可靠性

- 仅样式与 i18n 文案调整，零运行时开销与回归风险。
- 渐变文字通过 `bg-clip-text`，无需修改 tailwind 配置（`from-sky-*`/`via-sky-*`/`to-cyan-*` 为 Tailwind 内置色板）。