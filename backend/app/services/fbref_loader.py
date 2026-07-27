"""
FBref 球员数据抓取服务
=====================
从 FBref.com 抓取指定球员的 2025/26 赛季统计数据。
FBref 页面中表格被包装在 HTML 注释中，需要先解开注释再解析。

用法：
    from app.services.fbref_loader import fetch_player_stats
    stats = await fetch_player_stats("Erling Haaland")

注意：
  - FBref 有 Cloudflare 防护，需要真实浏览器环境（建议配合 Playwright 使用）
  - 本服务优先使用 pandas.read_html 解析（轻量），失败时返回 None
  - 建议在导入脚本中运行，而非实时查询
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Optional

import httpx
import pandas as pd

logger = logging.getLogger("fbref_loader")

# ── 请求配置 ──────────────────────────────────────────────
TIMEOUT = 30.0
RETRIES = 2
RETRY_DELAY = 2.0
REQUEST_INTERVAL = 3.0  # 请求间隔（秒），避免触发反爬
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

# ── 球员 → FBref URL 映射 ────────────────────────────────
# 键为 name_en，值为 FBref 球员页完整 URL
FBREF_URLS: dict[str, str] = {
    "Erling Haaland": "https://fbref.com/en/players/1f44ac21/Erling-Haaland",
    "Kylian Mbappé": "https://fbref.com/en/players/42fd9c7f/Kylian-Mbappe",
    "Harry Kane": "https://fbref.com/en/players/21a66f6a/Harry-Kane",
    "Robert Lewandowski": "https://fbref.com/en/players/8d78e732/Robert-Lewandowski",
    "Victor Osimhen": "https://fbref.com/en/players/8f9e077e/Victor-Osimhen",
    "Alexandre Lacazette": "https://fbref.com/en/players/62f1e90d/Alexandre-Lacazette",
    "Kevin De Bruyne": "https://fbref.com/en/players/d02f33e7/Kevin-De-Bruyne",
    "Jude Bellingham": "https://fbref.com/en/players/571e66d0/Jude-Bellingham",
    "Rodri": "https://fbref.com/en/players/245dc053/Rodri",
    "Luka Modrić": "https://fbref.com/en/players/6020f1e5/Luka-Modric",
    "Jamal Musiala": "https://fbref.com/en/players/2c0558b8/Jamal-Musiala",
    "Federico Chiesa": "https://fbref.com/en/players/ba06f7af/Federico-Chiesa",
    "Virgil van Dijk": "https://fbref.com/en/players/ec399823/Virgil-van-Dijk",
    "Rúben Dias": "https://fbref.com/en/players/6e3a7333/Ruben-Dias",
    "Antonio Rüdiger": "https://fbref.com/en/players/d42f21c5/Antonio-Rudiger",
    "Marquinhos": "https://fbref.com/en/players/4c67fe00/Marquinhos",
    "Theo Hernández": "https://fbref.com/en/players/6f2c47a5/Theo-Hernandez",
    "Thibaut Courtois": "https://fbref.com/en/players/5f3c45b7/Thibaut-Courtois",
    "Alisson": "https://fbref.com/en/players/7a2e46a8/Alisson",
    "Ederson": "https://fbref.com/en/players/dc5c9d60/Ederson",
    "Gianluigi Donnarumma": "https://fbref.com/en/players/f0e4e674/Gianluigi-Donnarumma",
    "Manuel Neuer": "https://fbref.com/en/players/00938f84/Manuel-Neuer",
}

# ── 字段映射：FBref 列名 → 本系统 stats 字段 ──────────────
# 每张表的映射关系
STANDARD_MAP = {
    "apps": "appearances",
    "min": "minutes_played",
    "gls": "goals",
    "ast": "assists",
    "crdy": "yellow_cards",
    "crdr": "red_cards",
}

SHOOTING_MAP = {
    "sh": "shots_total",
    "sot": "shots_on_target",
}

PASSING_MAP = {
    "cmp%": "pass_accuracy",
    "kp": "key_passes",
}

DEFENSE_MAP = {
    "tkl": "tackles",
    "int": "interceptions",
    "clr": "clearances",
    "blocks": "blocks",
}

POSSESSION_MAP = {
    "succ": "dribbles_completed",
}

MISC_MAP = {
    "fls": "fouls_committed",
    "fld": "fouls_drawn",
    "won": "aerial_duels_won",
}

GOALKEEPING_MAP = {
    "saves": "saves",
    "cs": "clean_sheets",
    "ga": "goals_conceded",
}

# 所有映射汇总
ALL_COL_MAPS = [
    ("Standard", STANDARD_MAP),
    ("Shooting", SHOOTING_MAP),
    ("Passing", PASSING_MAP),
    ("Defense", DEFENSE_MAP),
    ("Possession", POSSESSION_MAP),
    ("Misc", MISC_MAP),
    ("Goalkeeping", GOALKEEPING_MAP),
]

# 表名关键词（用于匹配 HTML 中的表 ID 或标题）
TABLE_KEYWORDS = {
    "Standard": "standard",
    "Shooting": "shooting",
    "Passing": "passing",
    "Defense": "defense",
    "Possession": "possession",
    "Misc": "misc",
    "Goalkeeping": "keeper",
}


async def _fetch_html(url: str) -> Optional[str]:
    """获取 FBref 页面 HTML（处理 JS 挑战重定向）"""
    for attempt in range(RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                timeout=TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
                if "Just a moment..." in html or "Enable JavaScript" in html:
                    logger.warning("FBref 返回了 JS 挑战页面（Cloudflare），抓取被拦截")
                    return None
                return html
        except Exception as exc:
            logger.warning("请求 FBref 失败 (attempt %d/%d): %s", attempt + 1, RETRIES + 1, exc)
            if attempt < RETRIES:
                await asyncio.sleep(RETRY_DELAY)
    return None


def _unwrap_comments(html: str) -> str:
    """
    解开 FBref 的 HTML 注释包裹。
    FBref 将部分表格用 <!-- 和 --> 注释包裹起来防止简单爬虫。
    """
    # 移除 HTML 注释标记
    unwrapped = re.sub(r'<!--', '', html)
    unwrapped = re.sub(r'-->', '', unwrapped)
    return unwrapped


def _find_season_row(df: pd.DataFrame, season_pattern: str = "2025-26") -> Optional[pd.Series]:
    """
    在 DataFrame 中查找指定赛季的行。
    FBref 的 "Season" 列格式如 "2025-26"。
    优先查找标记了 "Totals" 的合并行或赛季完全匹配的行。
    """
    # 先找第一列中匹配的行
    for idx, row in df.iterrows():
        first_cell = str(row.iloc[0]).strip()
        # 跳过空行和表头行
        if not first_cell or first_cell in ("Season", "Playing Time", "Standard", "Performance"):
            continue
        # 匹配赛季
        if season_pattern in first_cell or first_cell == season_pattern:
            return row
    logger.debug("未找到赛季行 '%s'", season_pattern)
    return None


def _parse_int(val) -> int:
    """安全转为整数"""
    try:
        return int(float(str(val).replace(",", "")))
    except (ValueError, TypeError):
        return 0


def _parse_float(val) -> float:
    """安全转为浮点数"""
    try:
        return float(str(val).replace(",", "").replace("%", ""))
    except (ValueError, TypeError):
        return 0.0


def _parse_pct(val) -> float:
    """解析百分比（如 '89.7' 或 '89.7%' → 89.7）"""
    try:
        return float(str(val).replace("%", "").replace(",", ""))
    except (ValueError, TypeError):
        return 0.0


async def fetch_player_stats(
    name_en: str,
    season: str = "2025-26",
) -> Optional[dict]:
    """
    从 FBref 抓取一名球员的 2025/26 完整统计数据。

    参数:
        name_en: 球员英文名（如 "Erling Haaland"），需在 FBREF_URLS 中
        season:  赛季标识，默认 "2025-26"

    返回:
        {
            "stats": {  # 20 项统计字段
                "appearances": ..., "minutes_played": ..., "goals": ...,
                "assists": ..., "shots_total": ..., "shots_on_target": ...,
                "pass_accuracy": ..., "key_passes": ..., "tackles": ...,
                "interceptions": ..., "clearances": ..., "blocks": ...,
                "saves": ..., "clean_sheets": ..., "goals_conceded": ...,
                "dribbles_completed": ..., "aerial_duels_won": ...,
                "fouls_committed": ..., "fouls_drawn": ...,
                "yellow_cards": ..., "red_cards": ...,
            },
            "current_club": "俱乐部名",
            "club_league": "联赛名",
        }
        失败时返回 None。
    """
    url = FBREF_URLS.get(name_en)
    if not url:
        logger.warning("未找到球员 %s 的 FBref URL 映射", name_en)
        return None

    logger.info("正在抓取 %s 的 2025/26 数据…", name_en)
    html = await _fetch_html(url)
    if not html:
        return None

    # 解开注释
    html = _unwrap_comments(html)

    result_stats: dict = {}
    current_club: Optional[str] = None
    club_league: Optional[str] = None

    try:
        # 用 pandas 解析所有表格
        tables = pd.read_html(html)

        for table_name, col_map in ALL_COL_MAPS:
            keyword = TABLE_KEYWORDS.get(table_name, "").lower()

            # 搜索匹配的表
            for tbl in tables:
                # 检查表是否匹配关键词
                df_str = str(tbl.columns.tolist()).lower() + str(tbl.iloc[:2].to_string()).lower()
                if keyword not in df_str:
                    continue

                row = _find_season_row(tbl, season)
                if row is not None:
                    for fbref_col, our_col in col_map.items():
                        # 在行中查找匹配的列
                        for col_name in tbl.columns:
                            if fbref_col.lower() in str(col_name).lower():
                                raw = row[col_name]
                                if our_col in ("pass_accuracy",):
                                    result_stats[our_col] = _parse_pct(raw)
                                elif our_col in ("goals_conceded",):
                                    # 失球可能用 GA 或 GA90
                                    val = _parse_int(raw)
                                    result_stats[our_col] = val if val > 0 else _parse_int(
                                        row.get("GA", row.get("GA90", 0)) if hasattr(row, 'get') else 0
                                    )
                                else:
                                    result_stats[our_col] = _parse_int(raw)
                    logger.debug("解析 %s 表 → %d 字段", table_name, len(result_stats))
                    break
            else:
                logger.debug("未找到 %s 表的 2025/26 数据", table_name)

        # 提取当前俱乐部和联赛
        for tbl in tables:
            df_str = str(tbl.to_string()).lower()
            if "club" in df_str and "league" in df_str:
                try:
                    for _, row_data in tbl.iterrows():
                        first = str(row_data.iloc[0]).strip()
                        if "club" in first.lower():
                            current_club = str(row_data.iloc[1]).strip() if len(row_data) > 1 else None
                        if "league" in first.lower():
                            club_league = str(row_data.iloc[1]).strip() if len(row_data) > 1 else None
                except Exception:
                    pass

    except Exception as exc:
        logger.error("解析 %s 的 FBref 数据时出错: %s", name_en, exc)
        return None

    if not result_stats.get("appearances") and not result_stats.get("goals"):
        logger.warning("未能从 FBref 解析出 %s 的有效统计", name_en)
        return None

    result_stats.setdefault("appearances", 0)
    result_stats.setdefault("minutes_played", 0)
    result_stats.setdefault("goals", 0)
    result_stats.setdefault("assists", 0)
    result_stats.setdefault("shots_total", 0)
    result_stats.setdefault("shots_on_target", 0)
    result_stats.setdefault("pass_accuracy", 0.0)
    result_stats.setdefault("key_passes", 0)
    result_stats.setdefault("tackles", 0)
    result_stats.setdefault("interceptions", 0)
    result_stats.setdefault("clearances", 0)
    result_stats.setdefault("blocks", 0)
    result_stats.setdefault("saves", 0)
    result_stats.setdefault("clean_sheets", 0)
    result_stats.setdefault("goals_conceded", 0)
    result_stats.setdefault("dribbles_completed", 0)
    result_stats.setdefault("aerial_duels_won", 0)
    result_stats.setdefault("fouls_committed", 0)
    result_stats.setdefault("fouls_drawn", 0)
    result_stats.setdefault("yellow_cards", 0)
    result_stats.setdefault("red_cards", 0)

    return {
        "stats": result_stats,
        "current_club": current_club,
        "club_league": club_league,
    }


async def fetch_all_players(
    name_list: list[str] | None = None,
    season: str = "2025-26",
) -> dict[str, Optional[dict]]:
    """
    批量抓取多名球员的数据。

    返回: {name_en: result_dict 或 None}
    """
    if name_list is None:
        name_list = list(FBREF_URLS.keys())

    results: dict[str, Optional[dict]] = {}
    for i, name in enumerate(name_list):
        try:
            results[name] = await fetch_player_stats(name, season)
        except Exception as exc:
            logger.error("抓取 %s 异常: %s", name, exc)
            results[name] = None

        # 限流
        if i < len(name_list) - 1:
            await asyncio.sleep(REQUEST_INTERVAL)

    success = sum(1 for v in results.values() if v is not None)
    logger.info("批量抓取完成：%d/%d 成功", success, len(name_list))
    return results


if __name__ == "__main__":
    # 测试单个球员
    async def test():
        result = await fetch_player_stats("Erling Haaland")
        if result:
            print("✅ 抓取成功：")
            for k, v in result["stats"].items():
                print(f"  {k}: {v}")
            print(f"  俱乐部: {result.get('current_club')}")
            print(f"  联赛: {result.get('club_league')}")
        else:
            print("❌ 抓取失败（可能是 Cloudflare 拦截）")

    asyncio.run(test())
