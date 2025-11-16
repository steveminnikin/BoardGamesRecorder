import os
import sys
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

if __package__ in (None, ""):
    sys.path.append(os.path.dirname(__file__))
    from database import Base  # type: ignore  # noqa: F401
else:
    from .database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    matches_won = relationship("Match", back_populates="winner", foreign_keys="Match.winner_id")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # BoardGameGeek integration fields
    bgg_id = Column(Integer, unique=True, index=True, nullable=True)
    year_published = Column(Integer, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    min_players = Column(Integer, nullable=True)
    max_players = Column(Integer, nullable=True)
    playing_time = Column(Integer, nullable=True)
    bgg_rating = Column(Float, nullable=True)
    is_from_bgg = Column(Boolean, default=False)
    last_synced = Column(DateTime, nullable=True)

    matches = relationship("Match", back_populates="game")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    date_played = Column(DateTime, default=datetime.utcnow)
    winner_id = Column(Integer, ForeignKey("players.id"))

    game = relationship("Game", back_populates="matches")
    winner = relationship("Player", back_populates="matches_won", foreign_keys=[winner_id])
