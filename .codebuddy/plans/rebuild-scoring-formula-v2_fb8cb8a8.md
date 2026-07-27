---
name: rebuild-scoring-formula-v2
overview: 按用户新规范重构评分：移除年龄/团队实力，权重 50/25/20/3/2；队长影响力同时考虑俱乐部和国家队队长；荣誉/奖项加入时间衰减；个人数据沿用现有位置核心指标并按位置归一化
todos:
  - id: update-scoring-engine
    content: 修改 scoring.py：新权重、移除 age_raw 和 team_strength_raw，队长任一层面按队长计
    status: completed
  - id: update-frontend-vue
    content: 修改 PowerRankingView.vue、i18n/index.ts、RadarCompare.vue，移除两维标签和过滤
    status: completed
  - id: update-frontend-static
    content: 修改 backend/app/static/app.js 中 BD_LABELS，移除两维
    status: completed
  - id: restart-backend
    content: kill 当前 uvicorn 进程并重启，触发所有球员评分重算
    status: completed
    dependencies:
      - update-scoring-engine
  - id: verify
    content: 验证前端不再显示年龄和团队实力维度，评分已按新公式更新
    status: completed
    dependencies:
      - restart-backend
      - update-frontend-vue
      - update-frontend-static
---

## Product Overview

调整 JackeyFootball 球员综合实力评分体系，采用新的五维加权公式，并移除原系统中的年龄和团队实力维度。

## Core Features

- 综合实力 = 个人数据 × 50% + 个人荣誉 × 25% + 团队荣誉 × 20% + 身价 × 3% + 队长影响力 × 2%
- 移除 `age_raw`（巅峰年龄）和 `team_strength_raw`（团队实力）两个维度
- 队长影响力评分同时考虑俱乐部和国家队：任一层面担任队长即按队长档计算
- 基于现有数据库字段做近似实现（不新增 schema），后端重启后自动重算所有球员评分
- 前端 Vue 和原生 JS 页面同步移除相关维度展示与标签

## Tech Stack

- 后端：Python + FastAPI，评分引擎位于 `backend/app/services/scoring.py`
- 前端：Vue 3 + TypeScript + vue-i18n
- 数据库：SQLite（现有字段足以支持近似方案）

## Implementation Approach

修改后端评分引擎中的权重字典、维度列表和 `breakdown_raw` 计算，去掉 `age_raw` 和 `team_strength_raw`；调整 `compute_leadership_score` 使其在任一层面为队长时取最高分档。启动时 `run_scoring_engine()` 会自动遍历所有球员重新计算并写入 `overall_score` 和 `score_breakdown`。同步更新前端 `BD_LABELS`、i18n `bd` 翻译和雷达图维度过滤，保证展示与新公式一致。

## Implementation Notes

- 队长字段：`is_captain` 在现有数据中已混合记录俱乐部/国家队队长身份，直接按其为队长处理；`is_vice_captain` 为副队长，非队长取默认值
- 数据库无需 schema 变更，`score_breakdown` 是运行时返回字段，不持久化
- 后端修改后需 kill 当前 uvicorn 进程（pid 27132）并重新启动，触发评分重算
- 不改动雷达图、排名列表之外的 UI 样式

## Architecture Design

- 评分引擎层：集中修改 `scoring.py`，维持单一责任
- API 层：无需改动，接口返回结构不变
- 前端展示层：移除两个维度标签，保持与后端返回字段一致

## Directory Structure

```
/Users/hc360/CodeBuddy/20260725211858/
├── backend/app/services/scoring.py          [MODIFY] 权重、维度、队长分档
├── frontend/src/views/PowerRankingView.vue  [MODIFY] BD_LABELS 移除两维
├── frontend/src/i18n/index.ts               [MODIFY] bd 翻译移除两维
├── frontend/src/components/RadarCompare.vue [MODIFY] 维度过滤逻辑
└── backend/app/static/app.js                [MODIFY] BD_LABELS 移除两维
```