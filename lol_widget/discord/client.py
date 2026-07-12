"""Pushes profile data to the Discord identity profile endpoint."""

from __future__ import annotations

import logging

import requests

log = logging.getLogger(__name__)


class DiscordApiError(Exception):
    pass


class DiscordClient:
    def __init__(self, application_id: str, user_id: str, bot_token: str, timeout: float = 10.0):
        self._url = (
            f"https://discord.com/api/v9/applications/{application_id}"
            f"/users/{user_id}/identities/0/profile"
        )
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bot {bot_token}",
                "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)",
            }
        )
        self._timeout = timeout

    def update_profile(self, payload: dict) -> None:
        resp = self._session.patch(self._url, json=payload, timeout=self._timeout)
        if not resp.ok:
            raise DiscordApiError(f"Discord PATCH failed ({resp.status_code}): {resp.text}")
        log.info("Discord widget updated successfully.")
