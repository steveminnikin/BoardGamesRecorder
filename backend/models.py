from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    matches_won = relationship("Match", back_populates="winner", foreign_keys="Match.winner_id")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    matches = relationship("Match", back_populates="game")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    date_played = Column(DateTime, default=datetime.utcnow)
    winner_id = Column(Integer, ForeignKey("players.id"))

    game = relationship("Game", back_populates="matches")
    winner = relationship("Player", back_populates="matches_won", foreign_keys=[winner_id])
