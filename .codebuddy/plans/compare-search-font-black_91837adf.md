---
name: compare-search-font-black
overview: 将 CompareView.vue 搜索框 placeholder 文字及候选球员按钮文字改为黑色，使其在白色卡片上可见。
todos:
  - id: fix-search-font-color
    content: 修改 CompareView.vue 搜索框与候选按钮文字为黑色
    status: completed
  - id: visual-verify
    content: 预览 /compare 确认黑色文字在白色卡片上可见
    status: completed
    dependencies:
      - fix-search-font-color
---

## 用户需求

截图中红圈圈出了球员对比页（/compare）白色卡片内的搜索区域：要求搜索框 placeholder 文字、候选球员按钮文字（未选中状态）全部改为黑色字体，在白色卡片背景上清晰可见。

## 产品概述

仅对 `CompareView.vue` 中搜索/候选球员按钮做一次颜色修正，不涉及结构或功能。

## 核心特性

- 搜索框 placeholder 改为黑色半透明。
- 搜索框输入文字改为黑色。
- 候选球员按钮未选中状态文字改为黑色、背景改为浅灰；选中状态保持白色文字。
- 位置筛选 chips（全部/前锋/中场/后卫/门将）本身颜色可独立处理，但保持现有深色风格以与标题区一致。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Tailwind CSS（现有项目）
- 无需新增依赖

## 实现方案

采用 Tailwind 颜色类修正，直接修改 `frontend/src/views/CompareView.vue` 中搜索框与候选按钮的文本色、背景色、边框色。

## 目录结构（受影响文件）

```
frontend/
└── src/
    └── views/
        └── CompareView.vue       # [MODIFY] 搜索框与候选按钮颜色改为黑色系
```

## 关键修改

- 搜索框：`class` 从 `text-white placeholder-white/50 border-white/20 bg-white/10 focus:border-white/40` 改为 `text-black placeholder-black/50 border-slate-200 bg-slate-100 focus:border-indigo-400`。
- 候选按钮未选中：从 `text-white/90 bg-white/10 hover:bg-white/20` 改为 `text-slate-800 bg-slate-100 hover:bg-slate-200`。
- 候选按钮选中：保持 `bg-indigo-600 text-white`。