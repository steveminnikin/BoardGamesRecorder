from sqlalchemy.orm import Session
from sqlalchemy import func
from backend import models, schemas

# Players
def get_players(db: Session):
    return db.query(models.Player).all()

def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(name=player.name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

# Games
def get_games(db: Session):
    return db.query(models.Game).all()

def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()

def create_game(db: Session, game: schemas.GameCreate):
    db_game = models.Game(name=game.name)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# Matches
def get_matches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Match).order_by(models.Match.date_played.desc()).offset(skip).limit(limit).all()

def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def create_match(db: Session, match: schemas.MatchCreate):
    db_match = models.Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_matches_with_details(db: Session, skip: int = 0, limit: int = 100):
    matches = db.query(
        models.Match.id,
        models.Game.name.label('game_name'),
        models.Player.name.label('winner_name'),
        models.Match.date_played
    ).join(
        models.Game, models.Match.game_id == models.Game.id
    ).join(
        models.Player, models.Match.winner_id == models.Player.id
    ).order_by(
        models.Match.date_played.desc()
    ).offset(skip).limit(limit).all()

    return [
        schemas.MatchWithDetails(
            id=m.id,
            game_name=m.game_name,
            winner_name=m.winner_name,
            date_played=m.date_played
        ) for m in matches
    ]

# Statistics
def get_game_stats(db: Session, game_id: int = None):
    if game_id:
        games = [db.query(models.Game).filter(models.Game.id == game_id).first()]
        if not games[0]:
            return []
    else:
        games = db.query(models.Game).all()

    stats = []
    for game in games:
        matches = db.query(models.Match).filter(models.Match.game_id == game.id).all()
        total_matches = len(matches)

        # Get the most recent match date
        last_played = None
        if matches:
            last_played = max(match.date_played for match in matches)

        player_stats = {}
        if total_matches > 0:
            players = db.query(models.Player).all()
            for player in players:
                wins = db.query(models.Match).filter(
                    models.Match.game_id == game.id,
                    models.Match.winner_id == player.id
                ).count()

                player_stats[player.name] = {
                    "wins": wins,
                    "win_rate": round((wins / total_matches) * 100, 1) if total_matches > 0 else 0
                }

        stats.append(schemas.GameStats(
            game_id=game.id,
            game_name=game.name,
            total_matches=total_matches,
            last_played=last_played,
            player_stats=player_stats
        ))

    return stats
