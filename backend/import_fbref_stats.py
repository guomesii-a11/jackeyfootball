"""
JackeyFootball FBref 真实统计数据导入脚本
==========================================
一次性脚本：从 FBref 抓取 22 名球员的 2025/26 赛季统计数据，
按 name_en 匹配并更新到现有数据库的 PlayerStats、current_club、club_league。

运行方式（在 backend/ 目录下）：
    cd backend
    python import_fbref_stats.py

可选环境变量：
    SKIP_SEED=1      跳过 mock seed（当数据库已存在球员时使用）
    FBREF_SEASON=2025-26  自定义赛季标识

注意：
  - FBref 有 Cloudflare 防护，直接抓取可能被拦截。
  - 建议在能运行 Playwright/Selenium 的环境中使用。
  - 如果实时抓取失败，会回退到 mock_data.py 中已更新的 2025/26 数据。
"""

import asyncio
import logging
import os
import sys

from app.database import Base, engine, SessionLocal
from app.models import Player, PlayerStats
from app.services.mock_data import seed_database, SEASON
from app.services.fbref_loader import fetch_all_players
from app.main import run_scoring_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("import_fbref_stats")


async def main() -> None:
    db = SessionLocal()
    try:
        # 1) 确保数据库已填充
        if db.query(Player).count() == 0 and os.getenv("SKIP_SEED") != "1":
            logger.info("数据库为空，先填充种子数据…")
            seed_database()

        players = db.query(Player).all()
        logger.info("准备为 %d 名球员更新 2025/26 真实统计…", len(players))

        # 2) 批量抓取
        name_list = [p.name_en for p in players]
        season_param = os.getenv("FBREF_SEASON", "2025-26")
        results = await fetch_all_players(name_list, season=season_param)

        # 3) 逐球员更新
        updated = 0
        skipped = 0
        failed = 0

        for p in players:
            result = results.get(p.name_en)
            if not result:
                logger.info("· %s 未获取到 FBref 数据，保留种子值", p.name_en)
                skipped += 1
                continue

            stats_data = result.get("stats", {})
            if not stats_data or not stats_data.get("appearances"):
                logger.info("· %s FBref 数据无效，保留种子值", p.name_en)
                skipped += 1
                continue

            # 更新或创建 PlayerStats
            if p.stats:
                # 更新已有记录
                for field, val in stats_data.items():
                    if hasattr(p.stats, field):
                        setattr(p.stats, field, val)
                p.stats.season = SEASON  # 使用 mock_data 的赛季标识
            else:
                # 创建新记录
                new_stats = PlayerStats(
                    player_id=p.id,
                    season=SEASON,
                    **stats_data,
                )
                db.add(new_stats)

            # 更新俱乐部信息
            if result.get("current_club"):
                p.current_club = result["current_club"]
            if result.get("club_league"):
                p.club_league = result["club_league"]

            updated += 1
            logger.info(
                "✓ %s → 出场=%s 进球=%s 助攻=%s",
                p.name_en,
                stats_data.get("appearances", "-"),
                stats_data.get("goals", "-"),
                stats_data.get("assists", "-"),
            )

        db.commit()
        logger.info(
            "导入完成：更新 %d 条，跳过 %d 条，失败 %d 条",
            updated, skipped, failed,
        )
    finally:
        db.close()

    # 4) 重跑评分引擎
    logger.info("重跑评分引擎…")
    run_scoring_engine()
    logger.info("全部完成。")


if __name__ == "__main__":
    asyncio.run(main())
