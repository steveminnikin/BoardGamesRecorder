"""
BoardGameGeek API Integration Module

This module handles all interactions with the BoardGameGeek (BGG) XML API,
including fetching user collections and synchronizing game data.
"""

import logging
import os
import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BGGIntegration:
    """Direct BoardGameGeek XML API integration with rate limiting."""

    BGG_API_BASE = "https://boardgamegeek.com/xmlapi2"

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize BGG API client.

        Args:
            api_token: Optional BGG API token for authentication.
                      If not provided, will try to read from BGG_API_TOKEN environment variable.
        """
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'BoardGamesRecorder/1.0'})

        # Set up API token if provided or available from environment
        token = api_token or os.environ.get('BGG_API_TOKEN')
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
            logger.info("BGG API token configured for authenticated requests")
        else:
            logger.warning("No BGG API token configured. API requests may be rate-limited or fail. "
                         "Register at https://boardgamegeek.com/applications to obtain a token.")

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
        max_retries: int = 5
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

        params = {
            'username': username,
            'subtype': 'boardgame',
            'stats': '1'
        }

        if owned_only:
            params['own'] = '1'

        for attempt in range(max_retries):
            try:
                self._rate_limit()

                response = self.session.get(
                    f"{self.BGG_API_BASE}/collection",
                    params=params,
                    timeout=30
                )

                # BGG returns 202 when collection is being generated
                if response.status_code == 202:
                    logger.info(f"Collection queued (attempt {attempt + 1}/{max_retries}). Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                if response.status_code == 200:
                    return self._parse_collection_xml(response.text)

                # Handle specific error codes
                if response.status_code == 401:
                    logger.error(
                        f"Access denied (401): BGG API requires authentication. "
                        f"Please register for API access at https://boardgamegeek.com/applications "
                        f"and set the BGG_API_TOKEN environment variable with your API token."
                    )
                    return None

                if response.status_code == 404:
                    logger.error(f"User '{username}' not found on BoardGameGeek")
                    return None

                logger.error(f"Unexpected status code: {response.status_code}")
                return None

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return None

            except Exception as e:
                logger.error(f"Error fetching collection: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return None

        logger.error(f"Failed to fetch collection after {max_retries} attempts")
        return None

    def _parse_collection_xml(self, xml_text: str) -> List[Dict]:
        """
        Parse BGG collection XML response.

        Args:
            xml_text: XML response from BGG API

        Returns:
            List of game dictionaries
        """
        games = []

        try:
            root = ET.fromstring(xml_text)

            for item in root.findall('item'):
                try:
                    game_data = self._extract_game_from_xml(item)
                    if game_data:
                        games.append(game_data)
                except Exception as e:
                    logger.warning(f"Error parsing game item: {e}")
                    continue

            logger.info(f"Successfully parsed {len(games)} games from XML")
            return games

        except ET.ParseError as e:
            logger.error(f"Error parsing XML: {e}")
            return []

    def _extract_game_from_xml(self, item: ET.Element) -> Optional[Dict]:
        """
        Extract game data from an XML item element.

        Args:
            item: XML Element representing a game

        Returns:
            Dictionary with game data or None if extraction fails
        """
        try:
            # Get basic info
            bgg_id = item.get('objectid')
            if not bgg_id:
                return None

            name_elem = item.find('name')
            name = name_elem.text if name_elem is not None else None

            if not name:
                return None

            # Get optional fields
            year_elem = item.find('yearpublished')
            year_published = int(year_elem.text) if year_elem is not None and year_elem.text else None

            thumbnail_elem = item.find('thumbnail')
            thumbnail_url = thumbnail_elem.text if thumbnail_elem is not None else None

            image_elem = item.find('image')
            image_url = image_elem.text if image_elem is not None else None

            # Get stats if available
            stats_elem = item.find('stats')
            min_players = None
            max_players = None
            playing_time = None
            bgg_rating = None

            if stats_elem is not None:
                min_players_elem = stats_elem.get('minplayers')
                max_players_elem = stats_elem.get('maxplayers')
                playing_time_elem = stats_elem.get('playingtime')

                min_players = int(min_players_elem) if min_players_elem else None
                max_players = int(max_players_elem) if max_players_elem else None
                playing_time = int(playing_time_elem) if playing_time_elem else None

                # Get average rating
                rating_elem = stats_elem.find('.//average')
                if rating_elem is not None and rating_elem.get('value'):
                    try:
                        rating_value = rating_elem.get('value')
                        bgg_rating = float(rating_value) if rating_value != 'N/A' else None
                    except (ValueError, TypeError):
                        bgg_rating = None

            game_data = {
                'bgg_id': int(bgg_id),
                'name': name,
                'year_published': year_published,
                'thumbnail_url': thumbnail_url,
                'image_url': image_url,
                'min_players': min_players,
                'max_players': max_players,
                'playing_time': playing_time,
                'bgg_rating': bgg_rating
            }

            return game_data

        except Exception as e:
            logger.error(f"Error extracting game data: {e}")
            return None


# Singleton instance for reuse across the application
_bgg_client = None

def get_bgg_client() -> BGGIntegration:
    """Get or create singleton BGG client instance."""
    global _bgg_client
    if _bgg_client is None:
        _bgg_client = BGGIntegration()
    return _bgg_client
