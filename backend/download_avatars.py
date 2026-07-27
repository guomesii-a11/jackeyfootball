"""
球员头像导入脚本
================
一次性脚本：复用 thesportsdb_client 从 TheSportsDB 免费层按 name_en 获取球员
头像（优先透明 cutout，其次 thumb），下载到 backend/app/static/avatars/ 本地目录，
并把解析出的本地路径按球员顺序写回 mock_data.py 的 image_url 字段。

设计要点：
  - 本地化存储：头像随项目打包，离线可用，不依赖第三方图床运行时可用性。
  - 幂等：已存在同名文件则跳过下载；重复运行安全。
  - 写回 mock_data.py：image_url 作为种子数据的一部分，重启/重导后头像不丢。
  - 下载失败或 TheSportsDB 无图时保留 image_url 为空，前端自动回退到首字母头像。
  - 同名消歧：SEARCH_OVERRIDES 用更精确的检索词命中真实球员（如 Rodri）。

运行方式（在 backend/ 目录下）：
    cd backend
    python download_avatars.py

可选环境变量：
    THESPORTSDB_API_KEY  个人 Key（默认 "3"，免费免注册）
"""

import asyncio
import os
import re

import httpx

from app.services.mock_data import MOCK_PLAYERS
from app.services.thesportsdb_client import search_player, REQUEST_INTERVAL

# 后端根目录（本脚本位于 backend/ 下）
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
AVATARS_DIR = os.path.join(BACKEND_DIR, "app", "static", "avatars")
MOCK_DATA_PATH = os.path.join(BACKEND_DIR, "app", "services", "mock_data.py")

# 检索词覆盖：部分球员昵称在 TheSportsDB 无法直检（如 "Rodri" 会误命中
# Jay Rodriguez），用可命中真实球员的检索词覆盖。value 为实际查询串。
SEARCH_OVERRIDES: dict[str, str] = {
    "Rodri": "Hernandez Cascante",       # 真实 Rodri = 曼城/西班牙/1996
    "Kylian Mbappé": "Kylian Mbappe",
    "Luka Modric": "Luka Modric",
    "N'Golo Kanté": "N'Golo Kante",
    "Vinicius Junior": "Vinicius Junior",
}


def slugify(name_en: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name_en.lower()).strip("-") or "player"


async def main() -> None:
    os.makedirs(AVATARS_DIR, exist_ok=True)

    resolved: list[str] = []  # 与 MOCK_PLAYERS 顺序一致的 image_url 列表

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for p in MOCK_PLAYERS:
            name = p["name_en"]
            query = SEARCH_OVERRIDES.get(name, name)
            try:
                info = await search_player(
                    query,
                    client=client,
                    prefer_club=p.get("current_club"),
                    prefer_nationality=p.get("nationality"),
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[查询异常] {name}: {exc}")
                resolved.append("")
                await asyncio.sleep(REQUEST_INTERVAL)
                continue

            remote = info.get("image_url") or ""
            local = ""
            if remote:
                fname = f"{slugify(name)}.{'png' if 'png' in remote.lower() else 'jpg'}"
                dest = os.path.join(AVATARS_DIR, fname)
                if os.path.exists(dest) and os.path.getsize(dest) > 0:
                    local = f"/static/avatars/{fname}"
                    print(f"[已存在] {name} -> {fname}")
                else:
                    try:
                        r = await client.get(remote)
                        r.raise_for_status()
                        ctype = (r.headers.get("content-type") or "").lower()
                        ext = "png" if "png" in ctype or "png" in remote.lower() else "jpg"
                        fname = f"{slugify(name)}.{ext}"
                        dest = os.path.join(AVATARS_DIR, fname)
                        with open(dest, "wb") as f:
                            f.write(r.content)
                        local = f"/static/avatars/{fname}"
                        print(f"[下载 OK] {name} -> {fname} ({len(r.content)} bytes)")
                    except Exception as exc:  # noqa: BLE001
                        print(f"[下载失败] {name}: {exc}，保留远程 URL")
                        local = remote
            else:
                print(f"[无头像] {name}（TheSportsDB 未返回图片）")

            resolved.append(local)
            await asyncio.sleep(REQUEST_INTERVAL)

    # 将解析出的 image_url 按球员顺序写回 mock_data.py
    with open(MOCK_DATA_PATH, encoding="utf-8") as f:
        text = f.read()

    it = iter(resolved)

    def _repl(_m: re.Match) -> str:
        return f'"image_url": "{next(it)}"'

    new_text = re.sub(r'"image_url":\s*"[^"]*"', _repl, text)

    with open(MOCK_DATA_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)

    ok = sum(1 for v in resolved if v)
    print(f"\n完成：{ok}/{len(resolved)} 名球员已写入头像路径，mock_data.py 已更新。")


if __name__ == "__main__":
    asyncio.run(main())
