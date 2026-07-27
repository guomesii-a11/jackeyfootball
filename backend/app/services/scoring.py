"""
JackeyFootball 球员综合实力评分引擎
按位置分组（前锋/中场/后卫/门将），同位置内对比。
评分因子（新公式）：
  1. 个人数据(同位置标准化)  — 50%
  2. 个人荣誉(按含金量加权+时间衰减) — 25%
  3. 团队荣誉(按FIFA赛事权重+时间衰减) — 20%
  4. 身价(标准化)            —  3%
  5. 队长影响力              —  2%
"""

from typing import List, Dict, Optional
from statistics import mean, stdev
import math


# ---- FIFA 赛事权重 ----
COMPETITION_WEIGHTS = {
    # 国家队赛事
    "world_cup": 100.0,              # 世界杯
    "continental_cup": 80.0,         # 洲际杯 (欧洲杯/美洲杯)
    "confederations_cup": 30.0,      # 联合会杯
    "nations_league": 35.0,          # 欧国联
    # 俱乐部赛事
    "champions_league": 75.0,        # 欧冠
    "club_world_cup": 45.0,          # 世俱杯
    "europa_league": 50.0,           # 欧联杯
    "top5_league": 60.0,             # 五大联赛冠军
    "domestic_cup": 40.0,            # 国内杯赛
    "domestic_super_cup": 25.0,      # 国内超级杯
    "uefa_super_cup": 30.0,          # 欧超杯
}

# ---- 个人奖项权重 ----
AWARD_WEIGHTS = {
    "ballon_dor": 100.0,             # 金球奖
    "fifa_best": 95.0,               # 国际足联最佳球员
    "uefa_best": 85.0,               # 欧足联最佳球员
    "european_golden_boot": 70.0,    # 欧洲金靴
    "world_cup_golden_boot": 65.0,   # 世界杯金靴
    "world_cup_golden_ball": 75.0,   # 世界杯金球
    "ucl_top_scorer": 55.0,          # 欧冠最佳射手
    "league_top_scorer": 50.0,       # 联赛最佳射手
    "domestic_cup_top_scorer": 30.0, # 国内杯赛最佳射手
    "yashin_award": 80.0,            # 雅辛奖（门将）
    "fifa_best_gk": 75.0,            # FIFA最佳门将
    "league_golden_glove": 45.0,     # 联赛金手套
    "pfa_player_of_year": 55.0,      # PFA年度最佳
    "golden_boy": 40.0,              # 金童奖
    "kopa_trophy": 45.0,             # 科帕奖
    "best_young_player": 35.0,       # 最佳年轻球员
    "team_of_season": 35.0,          # 赛季最佳阵容
    "player_of_month": 15.0,         # 月最佳
}

# ---- 位置核心指标及权重（按每90分钟 + 加权） ----
POSITION_CORE_STATS = {
    "forward": {
        "goals": 0.30,
        "assists": 0.20,
        "shots_on_target": 0.15,
        "dribbles_completed": 0.15,
        "key_passes": 0.15,
        "pass_accuracy": 0.05,
    },
    "midfielder": {
        "pass_accuracy": 0.25,
        "key_passes": 0.20,
        "assists": 0.15,
        "tackles": 0.15,
        "interceptions": 0.15,
        "goals": 0.10,
    },
    "defender": {
        "tackles": 0.20,
        "interceptions": 0.20,
        "clearances": 0.15,
        "blocks": 0.15,
        "aerial_duels_won": 0.15,
        "pass_accuracy": 0.15,
    },
    "goalkeeper": {
        "saves": 0.30,
        "clean_sheets": 0.25,
        "goals_conceded": 0.20,
        "pass_accuracy": 0.15,
        "aerial_duels_won": 0.10,
    },
}

# 雷达图6维度
RADAR_DIMENSIONS = {
    "forward": ["goals", "assists", "shots_on_target", "key_passes", "defensive_contrib", "market_value_euro"],
    "midfielder": ["goals", "assists", "pass_accuracy", "key_passes", "defensive_contrib", "market_value_euro"],
    "defender": ["tackles", "interceptions", "clearances", "blocks", "pass_accuracy", "market_value_euro"],
    "goalkeeper": ["saves", "clean_sheets", "pass_accuracy", "aerial_duels_won", "defensive_contrib", "market_value_euro"],
}

RADAR_DIMENSION_LABELS = {
    "goals": "goals",
    "assists": "assists",
    "shots_on_target": "shots_on_target",
    "key_passes": "key_passes",
    "defensive_contrib": "defensive_contrib",
    "market_value_euro": "market_value",
    "pass_accuracy": "pass_accuracy",
    "tackles": "tackles",
    "interceptions": "interceptions",
    "clearances": "clearances",
    "blocks": "blocks",
    "saves": "saves",
    "clean_sheets": "clean_sheets",
    "aerial_duels_won": "aerial_duels_won",
}

# 当前年份，用于时间衰减
CURRENT_YEAR = 2026


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """Min-Max 归一化到 0-100"""
    if max_val == min_val:
        return 50.0
    return ((value - min_val) / (max_val - min_val)) * 100.0


def safe_normalize(values: List[float]) -> List[float]:
    """安全归一化，处理全等值情况"""
    if len(values) <= 1:
        return [50.0] * len(values)
    mn, mx = min(values), max(values)
    if mx == mn:
        return [50.0] * len(values)
    return [((v - mn) / (mx - mn)) * 100.0 for v in values]


def _decay_factor(year_str: Optional[str], lambda_val: float) -> float:
    """根据年份计算时间衰减系数：e^(-lambda * n)"""
    if not year_str:
        return 1.0
    try:
        year = int(str(year_str)[:4])
        years_ago = max(0, CURRENT_YEAR - year)
        return math.exp(-lambda_val * years_ago)
    except (ValueError, TypeError):
        return 1.0


def compute_honor_score(honors: List[dict]) -> float:
    """集体冠军总分 = Σ(赛事权重 × 次数 × 时间衰减)"""
    total = 0.0
    for h in honors:
        weight = h.get("competition_weight", 0)
        count = h.get("count", 1)
        year = h.get("year")
        decay = _decay_factor(year, lambda_val=0.4)
        total += weight * count * decay
    return total


def compute_award_score(awards: List[dict]) -> float:
    """个人荣誉总分 = Σ(奖项权重 × 次数 × 时间衰减)"""
    total = 0.0
    for a in awards:
        weight = a.get("award_weight", 0)
        count = a.get("count", 1)
        year = a.get("year")
        decay = _decay_factor(year, lambda_val=0.5)
        total += weight * count * decay
    return total


def compute_stats_score(stats: dict, position: str) -> float:
    """位置核心数据加权得分（尽量按每90分钟标准化）"""
    core = POSITION_CORE_STATS.get(position, {})
    if not core:
        return 0.0

    minutes = max(stats.get("minutes_played", 0), 1)
    weighted_sum = 0.0

    for key, weight in core.items():
        val = stats.get(key, 0)
        if key == "pass_accuracy":
            # 传球成功率已经是百分比，不做 per90 转换
            normalized_val = float(val)
        elif key == "goals_conceded":
            # 失球是负向指标，按 per90 取负值
            normalized_val = -(float(val) / minutes) * 90.0
        else:
            # 其他指标按每90分钟
            normalized_val = (float(val) / minutes) * 90.0

        weighted_sum += normalized_val * weight

    return weighted_sum


def compute_market_value_score(market_value_euro: int) -> float:
    """身价取对数缩放"""
    return math.log(max(market_value_euro, 1), 10) * 20  # ~120-200M => ~160


def compute_age_score(age: int) -> float:
    """年龄因子：24-30岁为巅峰，偏离越远分数越低（已停用，保留函数兼容）"""
    if 24 <= age <= 30:
        return 100.0
    elif age < 24:
        return 100.0 - (24 - age) * 5.0
    else:
        return max(0.0, 100.0 - (age - 30) * 5.0)


def compute_leadership_score(
    is_captain: bool,
    is_vice_captain: bool,
) -> float:
    """队长影响力：俱乐部或国家队任一层面是队长即取最高档"""
    if is_captain:
        return 100.0
    elif is_vice_captain:
        return 80.0
    return 50.0


def compute_team_strength_score(club_score: float, nt_score: float) -> float:
    """团队实力加成（已停用，保留函数兼容）"""
    return (club_score + nt_score) / 2.0


def compute_overall_score(
    honors: List[dict],
    awards: List[dict],
    stats: dict,
    market_value_euro: int,
    age: int,
    position: str,
    is_captain: bool,
    is_vice_captain: bool,
    club_strength: float,
    nt_strength: float,
) -> Dict:
    """
    计算综合评分及各维度分解
    返回: breakdown_raw 字典
    """
    honor_raw = compute_honor_score(honors)
    award_raw = compute_award_score(awards)
    stats_raw = compute_stats_score(stats, position)
    mv_raw = compute_market_value_score(market_value_euro)
    leadership_raw = compute_leadership_score(is_captain, is_vice_captain)

    breakdown_raw = {
        "honor_raw": honor_raw,
        "award_raw": award_raw,
        "stats_raw": stats_raw,
        "market_value_raw": mv_raw,
        "leadership_raw": leadership_raw,
    }

    return breakdown_raw


def finalize_overall_score(breakdown_raw: Dict, position_group_norms: Dict) -> float:
    """
    用同位置组的 min/max 对各维度归一化，再加权求和
    返回: overall_score float
    """
    weights = {
        "stats_raw": 0.50,
        "award_raw": 0.25,
        "honor_raw": 0.20,
        "market_value_raw": 0.03,
        "leadership_raw": 0.02,
    }

    score = 0.0
    for dim, weight in weights.items():
        raw_val = breakdown_raw.get(dim, 0)
        norms = position_group_norms.get(dim, {"min": raw_val, "max": raw_val})
        normalized = normalize_value(raw_val, norms["min"], norms["max"])
        score += normalized * weight

    return round(min(score, 100.0), 1)


def compute_group_norms(all_breakdowns: List[Dict]) -> Dict:
    """计算同位置组各维度的 min/max"""
    dims = ["honor_raw", "award_raw", "stats_raw", "market_value_raw", "leadership_raw"]
    norms = {}
    for dim in dims:
        values = [b.get(dim, 0) for b in all_breakdowns]
        norms[dim] = {"min": min(values), "max": max(values)}
    return norms


def compute_radar_data(stats: dict, position: str, market_value_euro: int) -> Dict[str, float]:
    """
    计算雷达图6维度数据（原始值，前端归一化）
    """
    dims = RADAR_DIMENSIONS.get(position, RADAR_DIMENSIONS["forward"])

    radar = {}
    for dim in dims:
        if dim == "defensive_contrib":
            radar[dim] = stats.get("tackles", 0) + stats.get("interceptions", 0) + stats.get("clearances", 0) + stats.get("blocks", 0)
        elif dim == "market_value_euro":
            radar[dim] = market_value_euro
        elif dim == "goals_conceded":
            radar[dim] = -stats.get("goals_conceded", 0)
        else:
            radar[dim] = stats.get(dim, 0)

    return radar
