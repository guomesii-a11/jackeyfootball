from pydantic import BaseModel
from typing import Optional, List


# ---- Player Stats ----
class PlayerStatsSchema(BaseModel):
    season: str
    appearances: int = 0
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    shots_total: int = 0
    shots_on_target: int = 0
    pass_accuracy: float = 0.0
    key_passes: int = 0
    tackles: int = 0
    interceptions: int = 0
    clearances: int = 0
    blocks: int = 0
    saves: int = 0
    clean_sheets: int = 0
    goals_conceded: int = 0
    dribbles_completed: int = 0
    aerial_duels_won: int = 0

    class Config:
        from_attributes = True


# ---- Player Honor ----
class PlayerHonorSchema(BaseModel):
    honor_name: str
    honor_type: str
    competition_name: str
    competition_weight: float
    count: int = 1
    year: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Player Award ----
class PlayerAwardSchema(BaseModel):
    award_name: str
    award_weight: float
    count: int = 1
    year: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Player ----
class PlayerBase(BaseModel):
    name: str
    name_en: str
    position: str
    nationality: str
    age: int
    market_value_euro: int
    current_club: str
    club_league: str
    is_captain: bool = False
    is_vice_captain: bool = False
    national_team: str
    club_strength_score: float = 50.0
    national_team_strength_score: float = 50.0
    image_url: str = ""


class PlayerListItem(PlayerBase):
    id: int
    overall_score: float = 0.0

    class Config:
        from_attributes = True


class PlayerDetail(PlayerBase):
    id: int
    overall_score: float = 0.0
    stats: Optional[PlayerStatsSchema] = None
    honors: List[PlayerHonorSchema] = []
    awards: List[PlayerAwardSchema] = []
    score_breakdown: Optional[dict] = None

    class Config:
        from_attributes = True


class PlayerWithStats(PlayerListItem):
    """球员列表项附带基础数据 stats，供“各数据排名”页面使用。"""

    stats: Optional[PlayerStatsSchema] = None

    class Config:
        from_attributes = True


class PlayerCompareItem(BaseModel):
    id: int
    name: str
    name_en: str
    position: str
    age: int
    market_value_euro: int
    current_club: str
    overall_score: float
    stats: Optional[PlayerStatsSchema] = None
    radar_data: Optional[dict] = None

    class Config:
        from_attributes = True


# ---- Radar Chart Data ----
class RadarData(BaseModel):
    player_name: str
    dimensions: List[str]
    values: List[float]


class ComparisonResult(BaseModel):
    players: List[PlayerCompareItem]
    radar_data: List[RadarData]


# ---- Search ----
class PlayerSearchResult(BaseModel):
    id: int
    name: str
    name_en: str
    position: str
    current_club: str
    nationality: str

    class Config:
        from_attributes = True
