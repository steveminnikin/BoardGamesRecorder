import os
import sys
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

if __package__ in (None, ""):
    sys.path.append(os.path.dirname(__file__))
    import crud  # type: ignore  # noqa: F401
    import models  # type: ignore  # noqa: F401
    import schemas  # type: ignore  # noqa: F401
    from database import engine, get_db  # type: ignore  # noqa: F401
else:
    from . import crud, models, schemas
    from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Board Game Tracker")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Player endpoints
@app.get("/api/players", response_model=List[schemas.Player])
def read_players(db: Session = Depends(get_db)):
    return crud.get_players(db)

@app.post("/api/players", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    return crud.create_player(db, player)

@app.get("/api/players/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# Game endpoints
@app.get("/api/games", response_model=List[schemas.Game])
def read_games(db: Session = Depends(get_db)):
    return crud.get_games(db)

@app.post("/api/games", response_model=schemas.Game)
def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    return crud.create_game(db, game)

@app.get("/api/games/{game_id}", response_model=schemas.Game)
def read_game(game_id: int, db: Session = Depends(get_db)):
    db_game = crud.get_game(db, game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game

# Match endpoints
@app.get("/api/matches", response_model=List[schemas.MatchWithDetails])
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_matches_with_details(db, skip=skip, limit=limit)

@app.post("/api/matches", response_model=schemas.Match)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    # Validate game exists
    db_game = crud.get_game(db, match.game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    # Validate player exists
    db_player = crud.get_player(db, match.winner_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return crud.create_match(db, match)

@app.get("/api/matches/{match_id}", response_model=schemas.Match)
def read_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

# Statistics endpoints
@app.get("/api/stats", response_model=List[schemas.GameStats])
def read_all_stats(db: Session = Depends(get_db)):
    return crud.get_game_stats(db)

@app.get("/api/stats/{game_id}", response_model=schemas.GameStats)
def read_game_stats(game_id: int, db: Session = Depends(get_db)):
    stats = crud.get_game_stats(db, game_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Game not found")
    return stats[0]

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
