"""
BoardGameGeek API Integration Module

This module handles all interactions with the BoardGameGeek (BGG) API,
including fetching user collections and synchronizing game data.
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
from boardgamegeek import BGGClient
from boardgamegeek.exceptions import BGGValueError, BGGItemNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BGGIntegration:
    """Wrapper for BoardGameGeek API interactions with rate limiting and caching."""

    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize BGG client with caching.

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.client = BGGClient(cache='memory', ttl=cache_ttl)
        self.min_request_interval = 5  # BGG API rate limit: 5 seconds between requests
        self.last_request_time = 0

    def _rate_limit(self):
        """Ensure we don't exceed BGG API rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def fetch_user_collection(
        self,
        username: str,
        owned_only: bool = True,
        max_retries: int = 3
    ) -> Optional[List[Dict]]:
        """
        Fetch a user's board game collection from BGG.

        Args:
            username: BGG username
            owned_only: Only fetch owned games (default: True)
            max_retries: Maximum retry attempts for 202 responses

        Returns:
            List of game dictionaries with BGG data, or None if error
        """
        logger.info(f"Fetching collection for user: {username}")

        for attempt in range(max_retries):
            try:
                self._rate_limit()

                # Fetch collection with filters
                collection = self.client.collection(
                    user_name=username,
                    subtype='boardgame',  # Exclude expansions
                    own=owned_only
                )

                if collection is None:
                    logger.error(f"User '{username}' not found or collection is private")
                    return None

                # Convert collection items to dictionary format
                games = []
                for item in collection.items:
                    game_data = self._extract_game_data(item)
                    if game_data:
                        games.append(game_data)

                logger.info(f"Successfully fetched {len(games)} games for {username}")
                return games

            except BGGItemNotFoundError:
                logger.error(f"User '{username}' not found")
                return None

            except BGGValueError as e:
                logger.error(f"Invalid parameter: {e}")
                return None

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    sleep_time = (attempt + 1) * 5
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to fetch collection after {max_retries} attempts")
                    return None

        return None

    def _extract_game_data(self, item) -> Optional[Dict]:
        """
        Extract relevant game data from a BGG collection item.

        Args:
            item: BGG collection item object

        Returns:
            Dictionary with game data or None if extraction fails
        """
        try:
            game_data = {
                'bgg_id': item.id,
                'name': item.name,
                'year_published': getattr(item, 'year_published', None),
                'thumbnail_url': getattr(item, 'thumbnail', None),
                'image_url': getattr(item, 'image', None),
                'min_players': getattr(item, 'min_players', None),
                'max_players': getattr(item, 'max_players', None),
                'playing_time': getattr(item, 'playing_time', None),
            }

            # Try to get BGG rating if available
            try:
                stats = getattr(item, 'stats', None)
                if stats:
                    rating = getattr(stats, 'average', None)
                    game_data['bgg_rating'] = float(rating) if rating else None
            except (AttributeError, ValueError, TypeError):
                game_data['bgg_rating'] = None

            return game_data

        except Exception as e:
            logger.error(f"Error extracting game data: {e}")
            return None

    def get_game_details(self, game_id: int) -> Optional[Dict]:
        """
        Fetch detailed information for a specific game.

        Args:
            game_id: BGG game ID

        Returns:
            Dictionary with detailed game data or None if error
        """
        try:
            self._rate_limit()

            game = self.client.game(game_id=game_id)
            if not game:
                return None

            return {
                'bgg_id': game.id,
                'name': game.name,
                'year_published': getattr(game, 'year', None),
                'thumbnail_url': getattr(game, 'thumbnail', None),
                'image_url': getattr(game, 'image', None),
                'min_players': getattr(game, 'min_players', None),
                'max_players': getattr(game, 'max_players', None),
                'playing_time': getattr(game, 'playing_time', None),
                'bgg_rating': getattr(game, 'rating_average', None),
                'description': getattr(game, 'description', None),
            }

        except Exception as e:
            logger.error(f"Error fetching game {game_id}: {e}")
            return None


# Singleton instance for reuse across the application
_bgg_client = None

def get_bgg_client() -> BGGIntegration:
    """Get or create singleton BGG client instance."""
    global _bgg_client
    if _bgg_client is None:
        _bgg_client = BGGIntegration()
    return _bgg_client
