from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlayerBase(BaseModel):
    name: str

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None

class Player(PlayerBase):
    id: int

    class Config:
        from_attributes = True

class GameBase(BaseModel):
    name: str

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    name: Optional[str] = None

class Game(GameBase):
    id: int
    bgg_id: Optional[int] = None
    year_published: Optional[int] = None
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    playing_time: Optional[int] = None
    bgg_rating: Optional[float] = None
    is_from_bgg: bool = False
    last_synced: Optional[datetime] = None

    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    game_id: int
    winner_id: int
    date_played: Optional[datetime] = None

class MatchCreate(MatchBase):
    pass

class MatchUpdate(BaseModel):
    game_id: Optional[int] = None
    winner_id: Optional[int] = None
    date_played: Optional[datetime] = None

class Match(MatchBase):
    id: int
    date_played: datetime

    class Config:
        from_attributes = True

class MatchWithDetails(BaseModel):
    id: int
    game_name: str
    winner_name: str
    date_played: datetime

    class Config:
        from_attributes = True

class GameStats(BaseModel):
    game_id: int
    game_name: str
    total_matches: int
    last_played: Optional[datetime] = None
    player_stats: dict  # {player_name: {wins: int, win_rate: float}}

    class Config:
        from_attributes = True
