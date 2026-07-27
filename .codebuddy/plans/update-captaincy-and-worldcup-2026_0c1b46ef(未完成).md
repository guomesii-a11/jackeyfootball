---
name: update-captaincy-and-worldcup-2026
overview: 三件事：1) 在常量中补充"The Netherlands"→"荷兰"映射并给静态前端加国籍翻译；2) 修正 Rodri、Mbappé 等球员的国家队队长身份；3) 更新至2025/26赛季，西班牙夺2026世界杯，全员年龄+2，刷新数据并重算评分。
todos:
  - id: update-mock-data
    content: 修改 mock_data.py：赛季改为 2025/2026、全员年龄 +2、修正 7 人队长、罗德里新增 2026 世界杯冠军
    status: pending
  - id: fix-static-i18n
    content: 修改 static/app.js：新增 NATION_ZH_MAP 国籍翻译映射，rowHTML 和 detailHTML 中 nationality/national_team 替换为翻译调用
    status: pending
  - id: fix-constants-nl
    content: "修改 constants.ts：NATION_ZH_MAP 补充 'The Netherlands': '荷兰'"
    status: pending
  - id: rebuild-db-restart
    content: 删除 jackeyfootball.db，kill 并重启 uvicorn 触发重新种子与评分重算
    status: pending
    dependencies:
      - update-mock-data
  - id: verify-result
    content: 验证：国籍 "Netherlands" 显示为"荷兰"、罗德里为队长且有世界杯冠军、评分已更新
    status: pending
    dependencies:
      - rebuild-db-restart
      - fix-static-i18n
      - fix-constants-nl
---

