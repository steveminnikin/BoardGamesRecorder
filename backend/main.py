import os
import sys
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

try:
    # Normal package import when backend is available on PYTHONPATH
    from backend import crud, models, schemas
    from backend.database import engine, get_db
except ImportError:  # pragma: no cover - fallback for `python backend/main.py`
    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.append(str(backend_dir))
    import crud  # type: ignore  # noqa: F401
    import models  # type: ignore  # noqa: F401
    import schemas  # type: ignore  # noqa: F401
    from database import engine, get_db  # type: ignore  # noqa: F401

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

@app.put("/api/players/{player_id}", response_model=schemas.Player)
@app.patch("/api/players/{player_id}", response_model=schemas.Player)
def update_player(player_id: int, player_update: schemas.PlayerUpdate, db: Session = Depends(get_db)):
    db_player = crud.update_player(db, player_id, player_update)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

@app.delete("/api/players/{player_id}", status_code=204)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    try:
        deleted_player = crud.delete_player(db, player_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if deleted_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return None

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

@app.put("/api/games/{game_id}", response_model=schemas.Game)
@app.patch("/api/games/{game_id}", response_model=schemas.Game)
def update_game(game_id: int, game_update: schemas.GameUpdate, db: Session = Depends(get_db)):
    db_game = crud.update_game(db, game_id, game_update)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game

@app.delete("/api/games/{game_id}", status_code=204)
def delete_game(game_id: int, db: Session = Depends(get_db)):
    try:
        deleted_game = crud.delete_game(db, game_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if deleted_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return None

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

@app.put("/api/matches/{match_id}", response_model=schemas.Match)
@app.patch("/api/matches/{match_id}", response_model=schemas.Match)
def update_match(match_id: int, match_update: schemas.MatchUpdate, db: Session = Depends(get_db)):
    if match_update.game_id is not None:
        if crud.get_game(db, match_update.game_id) is None:
            raise HTTPException(status_code=404, detail="Game not found")
    if match_update.winner_id is not None:
        if crud.get_player(db, match_update.winner_id) is None:
            raise HTTPException(status_code=404, detail="Player not found")

    db_match = crud.update_match(db, match_id, match_update)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

@app.delete("/api/matches/{match_id}", status_code=204)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.delete_match(db, match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return None

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
