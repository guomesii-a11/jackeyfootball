"""
TheSportsDB 客户端
====================
封装 TheSportsDB 免费 API（v1）的球员查询，并将返回字段归一化映射为
本项目 Player 模型使用的字段。

数据源：https://www.thesportsdb.com/api/v1/json/{key}/searchplayers.php?p={name}
- 免费层默认测试 Key 为 "3"，无需注册即可调用；
- 如需更高额度/更全数据，可在 thesportsdb.com 通过 Patreon 订阅获取个人 Key，
  并写入 .env 的 THESPORTSDB_API_KEY 覆盖。

本客户端只负责"可免费获取"的真实字段：
  image_url（头像）、current_club（现俱乐部）、nationality（国籍）、
  national_team（国家队）、age（年龄）、position（位置）、name_en（英文名）。
身价 / 详细统计 / 荣誉等评分指标不在免费层范围内，由导入脚本保留原精选值。
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import Optional

import httpx

from ..config import settings

logger = logging.getLogger("thesportsdb")

BASE_URL = "https://www.thesportsdb.com/api/v1/json"
TIMEOUT = 15.0
RETRIES = 2
RETRY_DELAY = 1.0
REQUEST_INTERVAL = 0.3  # 免费层限流保护：请求间隔（秒）

# TheSportsDB 位置写法 → 本项目 position 枚举
_POSITION_MAP = {
    "forward": "forward",
    "foward": "forward",
    "striker": "forward",
    "attacker": "forward",
    "midfield": "midfielder",
    "midfielder": "midfielder",
    "defender": "defender",
    "goalkeeper": "goalkeeper",
    "keeper": "goalkeeper",
    "gk": "goalkeeper",
}


def _map_position(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    key = raw.strip().lower()
    return _POSITION_MAP.get(key)


def _calc_age(date_born: Optional[str]) -> Optional[int]:
    """由 YYYY-MM-DD 出生日期计算周岁年龄；解析失败返回 None。"""
    if not date_born:
        return None
    try:
        born = date.fromisoformat(date_born.strip()[:10])
    except ValueError:
        return None
    today = date.today()
    return (
        today.year
        - born.year
        - ((today.month, today.day) < (born.month, born.day))
    )


def _pick_image(player: dict) -> str:
    """优先取透明切割图 strCutout，其次 strThumb，再 strRender；均空返回 ''。"""
    for field in ("strCutout", "strThumb", "strRender"):
        val = player.get(field)
        if val and str(val).strip():
            return str(val).strip()
    return ""


async def search_player(
    name_en: str,
    client: Optional[httpx.AsyncClient] = None,
    prefer_club: Optional[str] = None,
    prefer_nationality: Optional[str] = None,
) -> dict:
    """
    查询 TheSportsDB 并返回归一化球员资料。

    当返回多个候选时，按以下规则打分择优选最匹配者，避免同名误匹配：
        strPlayer 精确匹配 name_en          +10
        strTeam == prefer_club             +5
        strNationality == prefer_nationality +5
        含头像（strThumb/strCutout/strRender）+2

    返回字段（查询失败或字段缺失时对应值为 None/''）：
        name_en, image_url, current_club, nationality,
        national_team, age, position
    """
    key = settings.THESPORTSDB_API_KEY or "3"
    url = f"{BASE_URL}/{key}/searchplayers.php"
    params = {"p": name_en}

    own_client = client is None
    client = client or httpx.AsyncClient(timeout=TIMEOUT)

    result: dict = {
        "name_en": name_en,
        "image_url": "",
        "current_club": None,
        "nationality": None,
        "national_team": None,
        "age": None,
        "position": None,
    }

    try:
        for attempt in range(RETRIES + 1):
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as exc:  # noqa: BLE001
                if attempt >= RETRIES:
                    logger.warning(
                        "查询 %s 失败（已重试 %d 次）：%s", name_en, RETRIES, exc
                    )
                    return result
                await asyncio.sleep(RETRY_DELAY)
        else:
            return result

        players = (data or {}).get("player") or []
        if not players:
            logger.info("TheSportsDB 未找到球员：%s", name_en)
            return result

        # 多候选时打分择优选最匹配者，避免同名误匹配（如 "Rodri" 误命中 Jay Rodriguez）
        def _score(p: dict) -> int:
            s = 0
            if p.get("strPlayer", "").strip().lower() == name_en.strip().lower():
                s += 10
            if prefer_club and (p.get("strTeam") or "").strip().lower() == prefer_club.strip().lower():
                s += 5
            if prefer_nationality and (p.get("strNationality") or "").strip().lower() == prefer_nationality.strip().lower():
                s += 5
            if any(p.get(f) for f in ("strThumb", "strCutout", "strRender")):
                s += 2
            return s

        player = max(players, key=_score)
        if _score(player) == 0:
            logger.info(
                "TheSportsDB 候选均无强匹配（%s），取首个：%s",
                name_en,
                players[0].get("strPlayer"),
            )

        result["image_url"] = _pick_image(player)
        result["current_club"] = (
            player.get("strTeam") or None
        )  # 现俱乐部（俱乐部层面）
        nat = player.get("strNationality") or None
        result["nationality"] = nat
        # 国家队：免费层无直接字段，以国籍近似（同名国家队）
        result["national_team"] = nat
        result["age"] = _calc_age(player.get("dateBorn"))
        result["position"] = _map_position(player.get("strPosition"))
    finally:
        if own_client and client is not None:
            await client.aclose()

    return result
