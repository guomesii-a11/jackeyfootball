"""
JackeyFootball FastAPI 入口文件

功能：
  1. 启动时自动建表、填充种子数据（如为空或 mock_data.py 已变更则自动重导）、运行评分引擎计算 overall_score
  2. 提供球员列表 API（支持按位置筛选、按综合实力排序）
  3. 提供球员详情 API（含评分维度分解 score_breakdown）

保存位置：backend/app/main.py
运行方式：
  cd backend
  uvicorn app.main:app --reload
  # 或
  python -m app.main
"""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, Base, get_db

# 静态前端目录：backend/app/static
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
from .models import Player
from .schemas import PlayerListItem, PlayerDetail, PlayerStatsSchema, PlayerWithStats
from .services.scoring import (
    compute_overall_score,
    compute_group_norms,
    finalize_overall_score,
    normalize_value,
)
from .services.mock_data import seed_database


# ---------------------------------------------------------------------------
# 评分引擎封装
# ---------------------------------------------------------------------------
# 评分维度（与 services/scoring.py 中保持一致）
_SCORE_DIMS = [
    "stats_raw",
    "award_raw",
    "honor_raw",
    "market_value_raw",
    "leadership_raw",
]


def _build_breakdowns(db: Session):
    """
    计算所有球员的原始评分分解，并按位置分组求出各维度 min/max。

    返回:
        breakdowns: {player_id: breakdown_raw_dict}
        norms:      {position: {dim: {"min": x, "max": y}}}
    """
    players = db.query(Player).all()

    breakdowns: dict = {}
    for p in players:
        honors = [
            {"competition_weight": h.competition_weight, "count": h.count, "year": h.year}
            for h in p.honors
        ]
        awards = [
            {"award_weight": a.award_weight, "count": a.count, "year": a.year}
            for a in p.awards
        ]
        stats = (
            PlayerStatsSchema.model_validate(p.stats).model_dump()
            if p.stats
            else {}
        )
        breakdowns[p.id] = compute_overall_score(
            honors=honors,
            awards=awards,
            stats=stats,
            market_value_euro=p.market_value_euro,
            age=p.age,
            position=p.position,
            is_captain=p.is_captain,
            is_vice_captain=p.is_vice_captain,
            club_strength=p.club_strength_score,
            nt_strength=p.national_team_strength_score,
        )

    # 按位置分组，计算组内各维度 min/max（用于同位置归一化）
    groups: dict = {}
    for p in players:
        groups.setdefault(p.position, []).append(breakdowns[p.id])
    norms = {pos: compute_group_norms(bds) for pos, bds in groups.items()}

    return breakdowns, norms


def _normalize_breakdown(breakdown_raw: dict, norms: dict) -> dict:
    """将原始分解按组内 min/max 归一化到 0-100，用于前端展示维度雷达/条形。"""
    out = {}
    for dim in _SCORE_DIMS:
        raw = breakdown_raw.get(dim, 0)
        n = norms.get(dim, {"min": raw, "max": raw})
        out[dim] = round(normalize_value(raw, n["min"], n["max"]), 1)
    return out


def run_scoring_engine() -> None:
    """运行评分引擎：计算每位球员的 overall_score 并写回数据库。"""
    db = SessionLocal()
    try:
        breakdowns, norms = _build_breakdowns(db)
        players = db.query(Player).all()
        for p in players:
            p.overall_score = finalize_overall_score(
                breakdowns[p.id], norms[p.position]
            )
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 启动生命周期
# ---------------------------------------------------------------------------
def _ensure_seed() -> None:
    """若数据库为空或 mock_data.py 被修改过，则重新填充种子数据。

    机制：用 mock_data.py 文件内容的 SHA256 哈希与 seed_meta 表中记录的上次
    哈希比对。一旦不一致（说明你手动改了年龄/身价等数据），就自动清空并重
    新导入，无需手动删库。
    """
    from .models import SeedMeta
    from .services.mock_data import seed_database, compute_mock_data_hash

    current_hash = compute_mock_data_hash()
    db = SessionLocal()
    try:
        meta = db.query(SeedMeta).filter(SeedMeta.key == "mock_data_hash").first()
        db_empty = db.query(Player).count() == 0
        hash_changed = (meta is None) or (meta.value != current_hash)

        if db_empty or hash_changed:
            seed_database()
            if meta is None:
                meta = SeedMeta(key="mock_data_hash", value=current_hash)
                db.add(meta)
            else:
                meta.value = current_hash
            db.commit()
            reason = "数据库为空" if db_empty else "mock_data.py 已变更"
            print(f"[{reason}] 已从 mock_data.py 重新导入种子数据。")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：建表 → 种子数据 → 评分引擎
    Base.metadata.create_all(bind=engine)
    _ensure_seed()
    run_scoring_engine()
    yield
    # 关闭时无需特殊处理


# ---------------------------------------------------------------------------
# App & 路由
# ---------------------------------------------------------------------------
app = FastAPI(title="JackeyFootball API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")


@router.get("/players", response_model=List[PlayerListItem])
def list_players(
    position: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """球员列表，可按位置筛选，默认按综合实力降序排列。"""
    query = db.query(Player)
    if position:
        query = query.filter(Player.position == position)
    players = query.order_by(Player.overall_score.desc()).all()
    return players


@router.get("/players/stats", response_model=List[PlayerWithStats])
def list_players_with_stats(
    position: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """球员列表（含基础数据 stats），供“各数据排名”逐项排名使用。"""
    query = db.query(Player)
    if position:
        query = query.filter(Player.position == position)
    players = query.order_by(Player.overall_score.desc()).all()
    return players


@router.get("/players/compare", response_model=List[PlayerDetail])
def list_players_compare(db: Session = Depends(get_db)):
    """返回全部球员的详情（含归一化 score_breakdown），供前端"全体对比"雷达图一次性取齐。"""
    players = db.query(Player).all()
    breakdowns, norms = _build_breakdowns(db)
    result = []
    for p in players:
        bd = breakdowns.get(p.id)
        breakdown_norm = (
            _normalize_breakdown(bd, norms[p.position]) if bd else None
        )
        detail = PlayerDetail.model_validate(p)
        detail.score_breakdown = breakdown_norm
        result.append(detail)
    return result


@router.get("/players/{player_id}", response_model=PlayerDetail)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """球员详情，包含 stats / honors / awards 以及评分维度分解。"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    breakdowns, norms = _build_breakdowns(db)
    bd = breakdowns.get(player.id)
    breakdown_norm = (
        _normalize_breakdown(bd, norms[player.position]) if bd else None
    )

    detail = PlayerDetail.model_validate(player)
    detail.score_breakdown = breakdown_norm
    return detail


app.include_router(router)


# ---------------------------------------------------------------------------
# 静态前端 & 页面路由
# ---------------------------------------------------------------------------
# 托管 CSS / JS 等静态资源（前端打包产物 index.html + /assets 与头像 /static）
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


def _serve_page():
    """返回前端单页应用入口（客户端按路径渲染列表/详情/对比等）。"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/")
def root():
    """根路径：若已构建前端则返回页面，否则返回 API 提示。"""
    if os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
        return _serve_page()
    return {"message": "JackeyFootball API is running", "docs": "/docs", "players_page": "/players"}


@app.get("/players")
def players_page():
    """球员列表页面（漂亮的 HTML 页面，而非 JSON）。"""
    return _serve_page()


@app.get("/players/{player_id}")
def player_detail_page(player_id: int):
    """球员详情页面（同一单页应用按路径渲染）。"""
    return _serve_page()


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    """SPA 兜底：未知前端路由回退 index.html（不干扰 /api、/docs、/static、/assets）。"""
    index = os.path.join(STATIC_DIR, "index.html")
    if full_path.startswith(("api/", "docs", "openapi.json", "redoc", "static/", "assets/")):
        raise HTTPException(status_code=404, detail="Not Found")
    if os.path.isfile(index):
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Frontend not built")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
