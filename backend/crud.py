import os
import sys
from datetime import datetime
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

if __package__ in (None, ""):
    sys.path.append(os.path.dirname(__file__))
    import models  # type: ignore  # noqa: F401
    import schemas  # type: ignore  # noqa: F401
    from bgg_integration import get_bgg_client  # type: ignore  # noqa: F401
else:
    from . import models, schemas
    from .bgg_integration import get_bgg_client

# Players
def get_players(db: Session):
    return db.query(models.Player).all()

def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def create_player(db: Session, player: schemas.PlayerCreate):
    existing = db.query(models.Player).filter(func.lower(models.Player.name) == player.name.lower()).first()
    if existing:
        raise ValueError("Player name already exists")

    db_player = models.Player(name=player.name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, player_id: int, player_update: schemas.PlayerUpdate):
    db_player = get_player(db, player_id)
    if not db_player:
        return None

    update_data = player_update.model_dump(exclude_unset=True)
    if "name" in update_data:
        duplicate = db.query(models.Player).filter(
            func.lower(models.Player.name) == update_data["name"].lower(),
            models.Player.id != player_id,
        ).first()
        if duplicate:
            raise ValueError("Player name already exists")

    for field, value in update_data.items():
        setattr(db_player, field, value)

    db.commit()
    db.refresh(db_player)
    return db_player

def delete_player(db: Session, player_id: int):
    db_player = get_player(db, player_id)
    if not db_player:
        return None

    try:
        db.delete(db_player)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Cannot delete player with existing matches") from exc

    return db_player

# Games
def get_games(db: Session):
    return db.query(models.Game).all()

def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()

def create_game(db: Session, game: schemas.GameCreate):
    existing = db.query(models.Game).filter(func.lower(models.Game.name) == game.name.lower()).first()
    if existing:
        raise ValueError("Game name already exists")

    db_game = models.Game(name=game.name)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def update_game(db: Session, game_id: int, game_update: schemas.GameUpdate):
    db_game = get_game(db, game_id)
    if not db_game:
        return None

    update_data = game_update.model_dump(exclude_unset=True)
    if "name" in update_data:
        duplicate = db.query(models.Game).filter(
            func.lower(models.Game.name) == update_data["name"].lower(),
            models.Game.id != game_id,
        ).first()
        if duplicate:
            raise ValueError("Game name already exists")

    for field, value in update_data.items():
        setattr(db_game, field, value)

    db.commit()
    db.refresh(db_game)
    return db_game

def delete_game(db: Session, game_id: int):
    db_game = get_game(db, game_id)
    if not db_game:
        return None

    try:
        db.delete(db_game)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Cannot delete game with existing matches") from exc

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

def update_match(db: Session, match_id: int, match_update: schemas.MatchUpdate):
    db_match = get_match(db, match_id)
    if not db_match:
        return None

    update_data = match_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_match, field, value)

    db.commit()
    db.refresh(db_match)
    return db_match

def delete_match(db: Session, match_id: int):
    db_match = get_match(db, match_id)
    if not db_match:
        return None

    db.delete(db_match)
    db.commit()
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

# BoardGameGeek Integration
def get_game_by_bgg_id(db: Session, bgg_id: int):
    """Get a game by its BoardGameGeek ID."""
    return db.query(models.Game).filter(models.Game.bgg_id == bgg_id).first()

def sync_games_from_bgg(db: Session, username: str) -> Dict:
    """
    Sync games from BoardGameGeek for a given username.

    Returns a dictionary with sync results:
    {
        'success': bool,
        'games_added': int,
        'games_updated': int,
        'errors': List[str],
        'total_games': int
    }
    """
    result = {
        'success': False,
        'games_added': 0,
        'games_updated': 0,
        'errors': [],
        'total_games': 0
    }

    try:
        # Fetch collection from BGG
        bgg_client = get_bgg_client()
        games_data = bgg_client.fetch_user_collection(username)

        if games_data is None:
            result['errors'].append(f"Failed to fetch collection for user '{username}'")
            return result

        result['total_games'] = len(games_data)
        current_time = datetime.utcnow()

        # Process each game
        for game_data in games_data:
            try:
                bgg_id = game_data.get('bgg_id')
                if not bgg_id:
                    result['errors'].append(f"Game missing BGG ID: {game_data.get('name', 'Unknown')}")
                    continue

                # Check if game already exists by BGG ID
                existing_game = get_game_by_bgg_id(db, bgg_id)

                if existing_game:
                    # Update existing game
                    existing_game.name = game_data.get('name', existing_game.name)
                    existing_game.year_published = game_data.get('year_published')
                    existing_game.thumbnail_url = game_data.get('thumbnail_url')
                    existing_game.image_url = game_data.get('image_url')
                    existing_game.min_players = game_data.get('min_players')
                    existing_game.max_players = game_data.get('max_players')
                    existing_game.playing_time = game_data.get('playing_time')
                    existing_game.bgg_rating = game_data.get('bgg_rating')
                    existing_game.is_from_bgg = True
                    existing_game.last_synced = current_time
                    result['games_updated'] += 1
                else:
                    # Check if a game with the same name exists (case-insensitive)
                    name_conflict = db.query(models.Game).filter(
                        func.lower(models.Game.name) == game_data.get('name', '').lower()
                    ).first()

                    if name_conflict:
                        # Update the existing game with BGG data
                        name_conflict.bgg_id = bgg_id
                        name_conflict.year_published = game_data.get('year_published')
                        name_conflict.thumbnail_url = game_data.get('thumbnail_url')
                        name_conflict.image_url = game_data.get('image_url')
                        name_conflict.min_players = game_data.get('min_players')
                        name_conflict.max_players = game_data.get('max_players')
                        name_conflict.playing_time = game_data.get('playing_time')
                        name_conflict.bgg_rating = game_data.get('bgg_rating')
                        name_conflict.is_from_bgg = True
                        name_conflict.last_synced = current_time
                        result['games_updated'] += 1
                    else:
                        # Create new game
                        new_game = models.Game(
                            name=game_data.get('name', 'Unknown'),
                            bgg_id=bgg_id,
                            year_published=game_data.get('year_published'),
                            thumbnail_url=game_data.get('thumbnail_url'),
                            image_url=game_data.get('image_url'),
                            min_players=game_data.get('min_players'),
                            max_players=game_data.get('max_players'),
                            playing_time=game_data.get('playing_time'),
                            bgg_rating=game_data.get('bgg_rating'),
                            is_from_bgg=True,
                            last_synced=current_time
                        )
                        db.add(new_game)
                        result['games_added'] += 1

            except Exception as e:
                error_msg = f"Error processing game {game_data.get('name', 'Unknown')}: {str(e)}"
                result['errors'].append(error_msg)
                continue

        # Commit all changes
        db.commit()
        result['success'] = True

    except Exception as e:
        db.rollback()
        result['errors'].append(f"Sync failed: {str(e)}")
        result['success'] = False

    return result
