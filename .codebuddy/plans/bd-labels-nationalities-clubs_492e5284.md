---
name: bd-labels-nationalities-clubs
overview: 修复评分维度分解 "bd." 前缀问题、删除联赛字段、扩展俱乐部中文映射（5支新队）、新增国籍中英映射并在所有视图按 locale 切换。
todos:
  - id: extend-constants-mapping
    content: 扩展 constants.ts：新增 5 支俱乐部 + NATION_ZH_MAP 及 nationalityOf 函数
    status: completed
  - id: remove-bd-prefix-and-league
    content: 改造 PowerRankingView.vue：BD/STAT 标签本地化双表、删除联赛字段、引入 nationalityOf 处理国籍
    status: completed
  - id: preview-verify
    content: 预览 /players 综合实力页验证所有修改生效
    status: completed
---

针对综合实力页面（/players）的中文显示修正：

1. 评分维度分解区域每个维度前缀 "bd." 需去掉（应直接显示"团队荣誉""个人荣誉"等）。
2. 球员副信息行去除联赛字段（"Real Madrid · La Liga · 27岁" → "皇家马德里 · 27岁"）。
3. 俱乐部中文映射新增 5 支球队：

- Chicago Fire → 芝加哥火焰队
- Neom → 新未来城体育
- Galatasaray → 加拉塔萨雷
- Paris SG → 巴黎圣日耳曼
- Fenerbahçe → 费内巴切

4. 国家/国家队字段也要翻译为中文（如 France → 法国、Spain → 西班牙、Poland → 波兰、Brazil → 巴西、Croatia → 克罗地亚、Belgium → 比利时 等）。

英文模式下所有维度、俱乐部、国籍应自动切换回英文。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Tailwind CSS + vue-i18n
- 集中映射策略：`frontend/src/constants.ts` 统一管理俱乐部/国家中英映射，提供 `clubNameOf()` / `nationalityOf()` 工具函数
- 评分维度/统计标签改为本地化对象直接取值，规避 vue-i18n 在 HMR 缓存下未命中 "bd.xxx" 路径的异常

## 关键修复点

- BD_LABELS / STAT_LABELS 由 `Record<string, string>`（i18n key 间接查表）改为 `{ zh: Record<...>, en: Record<...> }` 直接双表，模板使用 `BD_LABELS[locale]?.[k]` 直接取值，永久消除 "bd." 前缀残留
- 联赛字段 `p.club_league` 从副信息行彻底删除
- nationality / national_team 字段通过 `nationalityOf()` 按 locale 切换

## 性能与可靠性

- 仅前端常量扩展与视图字段调整，无网络请求或后端变更
- `clubNameOf()` / `nationalityOf()` 为纯函数 O(1)，无运行时开销

# Agent Extensions

本次任务不涉及任何 Agent Extensions，不输出 `<extensions>` 标签。