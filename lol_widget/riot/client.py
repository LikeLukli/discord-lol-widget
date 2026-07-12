"""Thin HTTP client for the Riot APIs (account, summoner, league, match)."""

from __future__ import annotations

import logging
import time

import requests

log = logging.getLogger(__name__)

# Match-v5 queue IDs, keyed by the league-v4 queue type used in the config.
QUEUE_IDS = {
    "RANKED_SOLO_5x5": 420,
    "RANKED_FLEX_SR": 440,
}


class RiotApiError(Exception):
    pass


class RiotClient:
    def __init__(self, api_key: str, platform: str, region: str, timeout: float = 10.0):
        self._session = requests.Session()
        self._session.headers["X-Riot-Token"] = api_key
        self._platform_base = f"https://{platform}.api.riotgames.com"
        self._region_base = f"https://{region}.api.riotgames.com"
        self._timeout = timeout

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        while True:
            resp = self._session.get(url, params=params, timeout=self._timeout)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "5"))
                log.warning("Rate limited by Riot API, waiting %ss...", retry_after)
                time.sleep(retry_after + 1)
                continue

            if not resp.ok:
                raise RiotApiError(f"Riot API error {resp.status_code}: {resp.text}")

            return resp.json()

    def resolve_puuid(self, game_name: str, tag_line: str) -> str:
        data = self._get(
            f"{self._region_base}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        )
        return data["puuid"]

    def get_summoner(self, puuid: str) -> dict:
        return self._get(f"{self._platform_base}/lol/summoner/v4/summoners/by-puuid/{puuid}")

    def get_league_entries(self, puuid: str) -> list[dict]:
        return self._get(f"{self._platform_base}/lol/league/v4/entries/by-puuid/{puuid}")

    def get_recent_match_ids(self, puuid: str, count: int, queue_id: int) -> list[str]:
        return self._get(
            f"{self._region_base}/lol/match/v5/matches/by-puuid/{puuid}/ids",
            params={"start": 0, "count": count, "queue": queue_id},
        )

    def get_latest_match_id(self, puuid: str, queue_id: int) -> str | None:
        """Cheap single-request check for the most recent match."""
        match_ids = self.get_recent_match_ids(puuid, count=1, queue_id=queue_id)
        return match_ids[0] if match_ids else None

    def get_match(self, match_id: str) -> dict:
        return self._get(f"{self._region_base}/lol/match/v5/matches/{match_id}")
