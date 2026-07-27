---
name: white-bg-black-text
overview: 按"白底用黑字、黑底用白字"规则，将球员对比页白色卡片内的搜索框与候选球员按钮字体全部改为黑色。
design:
  styleKeywords:
    - 高对比配色
    - 白底黑字
    - 现代极简
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
      - "#000000"
      - "#ffffff"
    background:
      - "#FFFFFF"
      - "#050608"
      - "#0A0C12"
    text:
      - "#000000"
      - "#FFFFFF"
      - "#000000"
    functional:
      - "#000000"
      - "#00e1ff"
      - "#EF4444"
todos:
  - id: fix-search-input-dark-text
    content: 将 CompareView.vue 搜索输入框颜色改为黑字黑边（白底卡片内）
    status: completed
  - id: fix-candidate-buttons-dark-text
    content: 将 CompareView.vue 候选球员按钮（未选中）颜色改为黑字黑底
    status: completed
    dependencies:
      - fix-search-input-dark-text
  - id: fix-selected-tags-dark-text
    content: 将 CompareView.vue 已选标签与前缀颜色改为白底黑字风格
    status: completed
    dependencies:
      - fix-candidate-buttons-dark-text
---

## 产品概述

按用户明确规则"白底用黑字，黑底用白字"修正球员对比页（/compare）：将位于白色卡片内的搜索框、占位文字、候选球员按钮文字、已选标签全部调整为黑色系，使其在白底上清晰可见。

## 核心特性

- 搜索输入框（含占位文字）：由 `text-white placeholder-white/50` 改为 `text-black placeholder-black/40`，背景与边框改用 `bg-black/5 border-black/20`，focus 状态 `border-black/40`。
- 候选球员按钮（未选中）：由 `bg-white/10 text-white/90 hover:bg-white/20` 改为 `bg-black/5 text-black hover:bg-black/10`，禁用态保留 `disabled:opacity-50`。
- 候选球员按钮（已选中）：保留紫底白字 `bg-indigo-600 text-white`（紫色背景仍配白字，符合规则）。
- "已选："前缀标签：改为 `text-black/50`。
- 已选球员标签：背景从 `bg-indigo-600/30` 改为 `bg-indigo-100`（浅紫），文字 `text-black`，×按钮 `text-black/60 hover:text-black`。
- 卡片外的标题、副标题、位置 chips、清空按钮、雷达图空状态提示等不在白底区域内，维持现有黑底白字不变。

## 边界与范围

- 仅修改 `frontend/src/views/CompareView.vue` 中包裹在 `bg-white` 卡片内的元素；其它视图（HomeView、PowerRankingView、DataRankingView）不受影响。
- 不改动后端逻辑、不改动雷达图组件（RadarCompare.vue）。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Tailwind CSS（沿用现有项目，技术栈不变）。
- 仅 Tailwind 原子类与少量内联样式调整，无新增依赖，Vite HMR 实时生效。

## 关键决策

1. **白底黑字统一化**：把卡片内统一抽象为"在白底容器内的子元素使用黑色系颜色变量"，避免逐个组件单独维护。
2. **保留选中态对比**：候选按钮选中时维持紫底白字，强调选中状态，方便用户在白底卡片上一眼识别。
3. **不破坏全局主题**：仅改白底卡片内部颜色，外层黑底页面与导航栏文字维持白色，保证整体主题一致性。

## 实现要点（执行细节）

- 通过 Tailwind `bg-black/5`、`text-black`、`placeholder-black/40`、`border-black/20`、`focus:border-black/40`、`hover:bg-black/10` 等类应用到对应 DOM。
- 已选标签使用 `bg-indigo-100` 提供与白底卡片同层系但更显眼的对比色，×按钮保留交互性。
- 不引入新组件、不修改 props 与事件，确保 Vite HMR 即时反映变更。

在保持整体黑色主题与玻璃拟态风格不变的前提下，遵循"白底用黑字、黑底用白字"的配色一致性规则，让球员对比页白色卡片内的搜索框与候选球员按钮在白底上清晰可读。视觉上保留紫底选中态对比，整体仍维持简洁现代的暗色 + 玻璃卡片风格。