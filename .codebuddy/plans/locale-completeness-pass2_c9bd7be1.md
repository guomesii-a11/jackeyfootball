---
name: locale-completeness-pass2
overview: 全面修复中文/英文模式遗漏：PowerRankingView 详情国家与统计标签走本地化、添加荣誉/奖项中英映射、SideNav/CompareView/DataRankingView 硬编码中文全部走 i18n。
todos:
  - id: extend-constants-honors-awards
    content: 扩展 constants.ts：新增 HONOR_ZH_MAP / AWARD_ZH_MAP 及 honorNameOf / awardNameOf 函数
    status: completed
  - id: extend-i18n-completeness
    content: 扩展 i18n/index.ts：sideNav/compare/data/common 缺失文案中英 keys
    status: completed
  - id: fix-powerranking-detail
    content: 修复 PowerRankingView.vue：详情 nationality、stats 标签、honor/award 走 locale
    status: completed
    dependencies:
      - extend-constants-honors-awards
  - id: convert-sidenav-i18n
    content: 改造 SideNav.vue：desc 改 descKey，模板走 t()
    status: completed
    dependencies:
      - extend-i18n-completeness
  - id: convert-compareview-i18n
    content: 改造 CompareView.vue：所有硬编码中文替换为 t()
    status: completed
    dependencies:
      - extend-i18n-completeness
  - id: convert-dataranking-i18n
    content: 改造 DataRankingView.vue：标题/副标题/loading/error 走 t()
    status: completed
    dependencies:
      - extend-i18n-completeness
  - id: verify-locale
    content: 预览中英文模式验证所有遗漏修复
    status: completed
    dependencies:
      - fix-powerranking-detail
      - convert-sidenav-i18n
      - convert-compareview-i18n
      - convert-dataranking-i18n
---

## 背景

经过前几轮国际化推进，球员名字、俱乐部、年份、年龄段显示已较为完整。但用户最新反馈仍发现两类显著遗漏，需一次性扫尾完成。

## 中文模式遗漏（截图 1：球员详情抽屉）

- 副信息 `detail.national_team` 仍显示英文 `Spain`，应为"西班牙"。
- 基础数据 stats 标签显示英文 keys（`season`/`appearances`/`minutes_played`/...），中文模式应显示`赛季`/`出场`/`分钟`/...。

## 英文模式遗漏（截图 2/3/4）

1. 左侧 SideNav 卡片描述文字仍是中文：

- "全部球员综合实力排名"
- "进球 / 助攻 / 传球逐项排名"
- "全体 / 跨位置雷达图对比"

2. CompareView 几乎全部文字仍是中文：标题"球员对比 · 综合数据"、副标题、搜索框 placeholder、"热门球员："、"已选："、空状态文案、"加载中…"、"加载球员数据失败"等。
3. DataRankingView 标题/副标题"各数据排名"/"全部球员按所选指标统一排名对比。"仍硬编码中文。
4. 球员的集体荣誉与个人奖项在英文模式下仍是中文（DB 存的是中文）。需补充中文→英文映射表并在英文模式应用。

## 用户收益

- 中英切换体验完整化，所有页面文案与数据库展示字段在不同语言下符合当地语言习惯。
- 球员荣誉国际化（即使后端只有中文，英文模式下也能呈现对应英文）。

## 实现要点

1. **`frontend/src/constants.ts` 新增映射表与函数**

- `HONOR_ZH_MAP`：约 16 项中文→英文 honor（世界杯冠军→World Cup Champion、欧冠冠军→UEFA Champions League Winner、西甲冠军→La Liga Winner 等），与 `honorNameOf(zh, locale)` 函数；中文模式直接返回原值，英文模式查表。
- `AWARD_ZH_MAP`：约 15 项中文→英文 award（金球奖→Ballon d'Or、科帕奖→Kopa Trophy、法甲金靴→Ligue 1 Golden Boot 等），与 `awardNameOf(zh, locale)` 函数。
- 与现有 `clubNameOf` / `nationalityOf` 风格保持一致。

2. **`frontend/src/views/PowerRankingView.vue` 修复**

- L135：`{{ detail.national_team }}` → `{{ nationalityOf(detail.national_team, locale) }}`。
- L147：`{{ STAT_LABELS[k] || k }}` → `{{ STAT_LABELS[locale]?.[k] || k }}`（之前漏掉此处，STAT_LABELS 已是双表）。
- L163 / L169：荣誉/奖项 `{{ h.honor_name }}` / `{{ a.award_name }}` → `{{ honorNameOf(h.honor_name, locale) }}` / `{{ awardNameOf(a.award_name, locale) }}`。
- 在 `<script setup>` 增加 `honorNameOf` / `awardNameOf` 的 import。

3. **`frontend/src/i18n/index.ts` 扩展**

- `sideNav` 节点新增 `powerDesc` / `dataDesc` / `compareDesc` 中英。
- `compare` 节点补全：`title` / `subtitle` / `searchPlaceholder` / `hotPlayers` / `selected` / `emptyTitle` / `emptyHint` / `loading` / `loadError` / `clear` 中英。
- `data` 节点补全：`title` / `subtitle` / `loading` / `loadError` 中英。
- `common` 节点补 `loadError`：'加载数据失败' / 'Failed to load data'。

4. **`frontend/src/components/SideNav.vue`**：`desc` 字段从字符串改为 `descKey`，模板 `{{ t(c.descKey) }}`。
5. **`frontend/src/views/CompareView.vue`**：替换所有硬编码中文为 `t(...)`；`error.value` 改用 `t('compare.loadError')`。
6. **`frontend/src/views/DataRankingView.vue`**：标题、副标题、loading、error 替换为 `t(...)`。

## 性能与可靠性

- 仅前端常量扩展与视图文案/字段替换，无网络或后端变更。
- 所有 helper 函数（`honorNameOf` / `awardNameOf`）为 O(1) 纯函数。
- HMR 即时生效，用户刷新即可。