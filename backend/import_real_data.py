"""
JackeyFootball 真实数据导入脚本
================================
一次性脚本：从 TheSportsDB 免费数据源拉取真实球员资料（头像 / 现俱乐部 /
国籍 / 国家队 / 年龄 / 位置），按 name_en 匹配并 upsert 到现有数据库，
最后重跑评分引擎。

设计要点：
  - 复用 main.py 中已有的 mock seed：先确保数据库已填充（否则先 seed），
    再遍历现有球员逐条补全真实字段，不破坏身价/统计/荣誉等评分指标。
  - 按 name_en 做 upsert，脚本可重复安全运行（幂等）。
  - 单个球员查询异常被捕获，跳过该球员保留原值，保证整体不中断。
  - 免费层限流保护：每次查询间隔 ~0.3s。

运行方式（在 backend/ 目录下）：
    cd backend
    python import_real_data.py

可选环境变量：
    THESPORTSDB_API_KEY  个人 Key（默认 "3"，免费免注册）
    SKIP_SEED=1         跳过 mock seed（当数据库已存在球员时使用）
"""

import asyncio
import logging
import os

import httpx
from sqlalchemy import select

from app.database import Base, engine, SessionLocal
from app.models import Player
from app.services.mock_data import seed_database
from app.services.thesportsdb_client import search_player, REQUEST_INTERVAL
from app.main import run_scoring_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("import_real_data")

# 检索词覆盖表：部分球员昵称在 TheSportsDB 无法直检（如 "Rodri" 只会命中
# Jay Rodriguez），用可命中真实球员的检索词覆盖。value 为实际查询串。
SEARCH_OVERRIDES: dict[str, str] = {
    "Rodri": "Hernandez Cascante",  # 真实 Rodri = 曼城/西班牙/1996
}


async def main() -> None:
    db = SessionLocal()
    try:
        # 1) 确保数据库已填充（复用 mock 的评分指标）
        if db.query(Player).count() == 0 and os.getenv("SKIP_SEED") != "1":
            logger.info("数据库为空，先填充示例（精选指标）数据…")
            seed_database()

        players = db.query(Player).all()
        logger.info("准备为 %d 名球员补全真实资料…", len(players))

        updated = 0
        skipped = 0
        failed = 0

        async with httpx.AsyncClient(timeout=15.0) as client:
            for p in players:
                try:
                    query = SEARCH_OVERRIDES.get(p.name_en, p.name_en)
                    info = await search_player(
                        query,
                        client=client,
                        prefer_club=p.current_club,
                        prefer_nationality=p.nationality,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("查询 %s 异常：%s（保留原值）", p.name_en, exc)
                    failed += 1
                    await asyncio.sleep(REQUEST_INTERVAL)
                    continue

                changed = False
                if info.get("image_url"):
                    p.image_url = info["image_url"]
                    changed = True
                if info.get("current_club"):
                    p.current_club = info["current_club"]
                    changed = True
                if info.get("nationality"):
                    p.nationality = info["nationality"]
                    changed = True
                if info.get("national_team"):
                    p.national_team = info["national_team"]
                    changed = True
                if info.get("age") is not None:
                    p.age = info["age"]
                    changed = True
                if info.get("position"):
                    p.position = info["position"]
                    changed = True

                if changed:
                    updated += 1
                    logger.info(
                        "✓ %s → 俱乐部=%s 国籍=%s 年龄=%s 位置=%s 头像=%s",
                        p.name_en,
                        p.current_club,
                        p.nationality,
                        p.age,
                        p.position,
                        "有" if p.image_url else "无",
                    )
                else:
                    skipped += 1
                    logger.info("· %s 无新增真实字段，保留原值", p.name_en)

                await asyncio.sleep(REQUEST_INTERVAL)

        db.commit()
        logger.info(
            "导入完成：更新 %d 条，跳过 %d 条，失败 %d 条",
            updated,
            skipped,
            failed,
        )
    finally:
        db.close()

    # 2) 重跑评分引擎（真实字段变化不影响评分逻辑，但确保分数一致）
    logger.info("重跑评分引擎…")
    run_scoring_engine()
    logger.info("全部完成。")


if __name__ == "__main__":
    asyncio.run(main())
