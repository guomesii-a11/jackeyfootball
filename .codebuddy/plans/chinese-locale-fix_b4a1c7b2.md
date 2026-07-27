---
name: chinese-locale-fix
overview: 修复中文模式下球员名字、俱乐部名、年龄、身价、统计标签的中文显示问题：DataRankingView 无中英切换、俱乐部名无中文、年龄硬编码"岁"、多处标签未走 i18n。
todos:
  - id: create-constants
    content: 新建 constants.ts：俱乐部中英映射表 + clubNameOf 函数
    status: completed
  - id: extend-i18n
    content: 扩展 i18n/index.ts：新增 ageUnit、stats、bd、dataMetrics、power 中英 keys
    status: completed
  - id: fix-dataranking
    content: 改造 DataRankingView：引入 nameOf/clubNameOf、名字俱乐部本地化、指标标签 i18n
    status: completed
    dependencies:
      - create-constants
      - extend-i18n
  - id: fix-powerranking
    content: 改造 PowerRankingView：俱乐部名本地化、年龄后缀 i18n、标签走 i18n
    status: completed
    dependencies:
      - create-constants
      - extend-i18n
  - id: verify-all
    content: 预览所有页面验证中英文切换完整
    status: completed
    dependencies:
      - fix-dataranking
      - fix-powerranking
---

## 用户需求

中文版模式下所有球员的名字、俱乐部、年龄均为中文显示；英文模式下显示英文对应内容。身价保持欧元格式不变。

## 核心特性

- DataRankingView 新增 `nameOf()` 按 locale 切换球员中/英文名，俱乐部名通过前缀映射表转为中文
- PowerRankingView 年龄后缀 `岁` / `y` 按 locale 切换，俱乐部名中文化，统计标签与评分维度标签中英对照
- CompareView 名字已有 `nameOf()` 切换，本轮无改动
- 新建 `constants.ts` 存放 22 个俱乐部中英映射表及 `clubNameOf()` 工具函数
- 扩展 i18n 文案：年龄单位、统计标签、评分维度标签、数据指标标签、综合实力标题

## 技术栈

- 前端：Vue 3 + TypeScript + Tailwind CSS + vue-i18n
- 无新增依赖

## 实现方案

采用"集中映射 + i18n 扩展"策略：

1. 俱乐部名通过常量映射表 `CLUB_ZH_MAP` 在 `constants.ts` 中维护，`clubNameOf(en)` 按当前 locale 返回中文或英文原名
2. 统计标签/评分维度/数据指标从硬编码中文字符串迁移到 i18n messages，各视图通过 `$t('stats.xxx')` 按 locale 获取对应语言
3. 年龄后缀走 `$t('ageUnit')` 实现 `zh: '岁' | en: 'y'`

## 目录结构（受影响文件）

```
frontend/
└── src/
    ├── constants.ts               # [NEW] 俱乐部中文映射 + clubNameOf()
    ├── i18n/
    │   └── index.ts               # [MODIFY] 新增 ageUnit/stats/bd/data.metrics/power keys
    └── views/
        ├── DataRankingView.vue    # [MODIFY] nameOf/clubNameOf/指标标签 i18n
        └── PowerRankingView.vue   # [MODIFY] clubNameOf/ageUnit/标签 i18n
```

## 关键代码结构

### constants.ts — 俱乐部映射

```ts
import { useI18n } from 'vue-i18n'

export const CLUB_ZH_MAP: Record<string, string> = {
  'Manchester City': '曼彻斯特城',
  'Real Madrid': '皇家马德里',
  'Paris Saint-Germain': '巴黎圣日耳曼',
  // ... 共 22 个
}

export function clubNameOf(en: string): string {
  // 仅在 setup/组件内使用 locale 判断；纯函数版返回映射或原文
  return CLUB_ZH_MAP[en] || en
}
```

### i18n 新增 keys（节选）

```ts
zh: {
  ageUnit: '岁',
  power: { allRank: '全部球员综合实力排名' },
  stats: { season: '赛季', appearances: '出场', goals: '进球', /* ... */ },
  bd: { honor_raw: '团队荣誉', award_raw: '个人荣誉', /* ... */ },
  dataMetrics: { goals: '进球', assists: '助攻', /* ... */ },
}
en: {
  ageUnit: 'y',
  power: { allRank: 'All Players Power Ranking' },
  stats: { season: 'Season', appearances: 'Apps', goals: 'Goals', /* ... */ },
  bd: { honor_raw: 'Team Honors', award_raw: 'Individual Awards', /* ... */ },
  dataMetrics: { goals: 'Goals', assists: 'Assists', /* ... */ },
}
```

### 各视图修改要点

**DataRankingView.vue**

- 引入 `useI18n` 获取 `{ t, locale }`，新增 `nameOf(p)` 函数（按 locale 返回 `p.name` / `p.name_en`）
- 引入 `clubNameOf`，第 126 行 `p.current_club` → `clubNameOf(p.current_club)`
- metrics 数组 label 改为从 `t('dataMetrics.xxx')` 动态获取
- 第 124 行 `p.name_en` → `nameOf(p)`

**PowerRankingView.vue**

- 第 96/124 行 `p.current_club` / `detail.current_club` → 引入 `clubNameOf` 按 locale 切换
- 第 96 行 `p.age }}岁` → `{{ p.age }}{{ t('ageUnit') }}`
- STAT_LABELS/BD_LABELS 改为通过 `t('stats.xxx')` / `t('bd.xxx')` 从 i18n 取值
- 第 75 行硬编码"全部球员综合实力排名" → `{{ t('power.allRank') }}`