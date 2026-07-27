from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class Position(str, enum.Enum):
    FORWARD = "forward"
    MIDFIELDER = "midfielder"
    DEFENDER = "defender"
    GOALKEEPER = "goalkeeper"


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="中文名")
    name_en = Column(String(100), nullable=False, comment="英文名")
    position = Column(String(20), nullable=False, comment="位置: forward/midfielder/defender/goalkeeper")
    nationality = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    market_value_euro = Column(Integer, nullable=False, comment="身价（欧元）")
    current_club = Column(String(100), nullable=False)
    club_league = Column(String(50), nullable=False, comment="联赛: Premier League/La Liga etc.")
    is_captain = Column(Boolean, default=False)
    is_vice_captain = Column(Boolean, default=False)
    national_team = Column(String(50), nullable=False)
    club_strength_score = Column(Float, default=50.0, comment="俱乐部实力评分 0-100")
    national_team_strength_score = Column(Float, default=50.0, comment="国家队实力评分 0-100")
    overall_score = Column(Float, default=0.0, comment="综合实力评分 0-100")
    image_url = Column(String(500), default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    stats = relationship("PlayerStats", back_populates="player", uselist=False)
    honors = relationship("PlayerHonor", back_populates="player")
    awards = relationship("PlayerAward", back_populates="player")


class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), unique=True, nullable=False)
    season = Column(String(9), nullable=False, comment="赛季 e.g. 2024/2025")
    appearances = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    shots_total = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    pass_accuracy = Column(Float, default=0.0, comment="传球成功率 %")
    key_passes = Column(Integer, default=0)
    tackles = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    clearances = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    saves = Column(Integer, default=0, comment="扑救（门将）")
    clean_sheets = Column(Integer, default=0, comment="零封（门将）")
    goals_conceded = Column(Integer, default=0, comment="失球（门将）")
    dribbles_completed = Column(Integer, default=0, comment="成功过人")
    aerial_duels_won = Column(Integer, default=0, comment="空中对抗胜出")
    fouls_committed = Column(Integer, default=0)
    fouls_drawn = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    player = relationship("Player", back_populates="stats")


class PlayerHonor(Base):
    __tablename__ = "player_honors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    honor_name = Column(String(200), nullable=False, comment="荣誉名称")
    honor_type = Column(String(20), nullable=False, comment="冠军类型: national_team/club")
    competition_name = Column(String(100), nullable=False, comment="赛事名称")
    competition_weight = Column(Float, nullable=False, comment="FIFA 赛事权重")
    count = Column(Integer, default=1)
    year = Column(String(20), comment="获奖年份")

    player = relationship("Player", back_populates="honors")


class PlayerAward(Base):
    __tablename__ = "player_awards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    award_name = Column(String(200), nullable=False, comment="个人荣誉名称")
    award_weight = Column(Float, nullable=False, comment="奖项含金量权重")
    count = Column(Integer, default=1)
    year = Column(String(20), comment="获奖年份")

    player = relationship("Player", back_populates="awards")


class SeedMeta(Base):
    """种子数据元数据：记录最近一次导入 mock_data.py 的内容哈希，用于检测数据是否变更。"""

    __tablename__ = "seed_meta"

    key = Column(String(50), primary_key=True)
    value = Column(String(255), nullable=False)
