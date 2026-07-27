---
name: rebuild-scoring-formula
overview: 移除 age_raw 和 team_strength_raw 两个维度，更新评分权重为：个人数据 50%、个人荣誉 25%、团队荣誉 20%、身价 3%、队长影响力 2%
todos:
  - id: update-scoring-engine
    content: 修改 scoring.py：更新权重字典、维度列表、breakdown_raw，去掉 age_raw 和 team_strength_raw
    status: pending
  - id: update-frontend-vue
    content: 修改 PowerRankingView.vue BD_LABELS、i18n/index.ts bd、RadarCompare.vue 维度过滤，去掉两个维度
    status: pending
  - id: update-frontend-static
    content: 修改 backend/app/static/app.js 中 BD_LABELS，去掉 age_raw 和 team_strength_raw
    status: pending
  - id: restart-backend
    content: kill 当前 uvicorn 进程并重启，触发评分重算
    status: pending
    dependencies:
      - update-scoring-engine
  - id: verify
    content: 验证前端不再显示年龄和团队实力维度，评分数值已按新公式更新
    status: pending
    dependencies:
      - restart-backend
      - update-frontend-vue
      - update-frontend-static
---

修改球员综合实力评分公式，移除"巅峰年龄"和"团队实力"两个维度，采用新权重：

- 个人数据 (stats_raw)：**50%**
- 个人荣誉 (award_raw)：**25%**
- 团队荣誉 (honor_raw)：**20%**
- 身价 (market_value_raw)：**3%**
- 队长影响力 (leadership_raw)：**2%**

涉及后端评分引擎重算、前端 Vue 和原生 JS 页面展示同步更新，修改后需重启 backend 服务使新评分生效。

## 技术栈

- 后端：Python / FastAPI (uvicorn 直接运行)
- 前端（Vue）：Vue 3 + TypeScript + vue-i18n
- 前端（原生 JS）：直接 HTML/JS 无构建依赖

## 方案概述

修改评分引擎 `scoring.py` 中的权重字典和维度列表，移除 `age_raw` 和 `team_strength_raw` 两个维度的计算与归一化调用；同步更新前端 Vue 和原生 JS 中所有引用这两个维度的标签数据和 i18n 翻译；最后重启 uvicorn 进程使评分重算生效。

关键决策：

- 保留 `compute_age_score()` 和 `compute_team_strength_score()` 函数体不动（函数本身仍存在），仅在 `compute_overall_score()` 中不再调用它们
- 修改后启动时 `run_scoring_engine()` 自动遍历所有球员、重新计算并写入数据库

## 改动点一览

| 文件 | 改动内容 |
| --- | --- |
| `backend/app/services/scoring.py` | weights 字典、dims 列表、breakdown_raw 字典 |
| `frontend/src/views/PowerRankingView.vue` | BD_LABELS 去掉两个维度 |
| `frontend/src/i18n/index.ts` | bd 翻译去掉两个维度 |
| `frontend/src/components/RadarCompare.vue` | 雷达过滤改为过滤两个维度 |
| `backend/app/static/app.js` | BD_LABELS 去掉两个维度 |


## 执行注意事项

- 后端改动后需 kill 当前 uvicorn 进程（pid 27132）再重新启动
- 重启后 run_scoring_engine() 自动重算所有球员评分并写入 DB
- 无需改数据库 schema，score_breakdown 是运行时返回字段，不持久化

## Agent Extensions

### SubAgent

- **code-explorer**: 已在前期探索阶段使用，用于扫描评分引擎和相关前端文件，确认所有需要修改的文件位置和代码逻辑。