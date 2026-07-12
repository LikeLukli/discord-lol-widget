"""Settings loading: config.yaml for behavior, environment/.env for secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv

DEFAULT_CONFIG_PATH = "config.yaml"


@dataclass(frozen=True)
class Secrets:
    riot_api_key: str
    discord_application_id: str
    discord_user_id: str
    discord_bot_token: str


@dataclass(frozen=True)
class RiotSettings:
    platform: str  # e.g. "euw1"
    region: str  # e.g. "europe"
    puuid: str | None
    game_name: str | None
    tag_line: str | None
    ranked_queue: str  # e.g. "RANKED_SOLO_5x5"
    matches_for_kda: int


@dataclass(frozen=True)
class DiscordSettings:
    title_suffix: str
    field_names: dict[str, str]


@dataclass(frozen=True)
class BehaviorSettings:
    update_mode: str  # "on_new_match" or "interval"
    check_interval_seconds: int
    update_interval_seconds: int
    max_staleness_seconds: int  # on_new_match: force a refresh after this long; 0 disables


@dataclass(frozen=True)
class IconSettings:
    rank_base: str
    role_base: str
    profile_icon_base: str


@dataclass(frozen=True)
class Settings:
    config_path: str
    secrets: Secrets
    riot: RiotSettings
    discord: DiscordSettings
    behavior: BehaviorSettings
    icons: IconSettings


def load_settings(config_path: str | None = None) -> Settings:
    load_dotenv()
    path = config_path or os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH)

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    riot = cfg["riot"]
    behavior = cfg.get("behavior", {})

    return Settings(
        config_path=path,
        secrets=Secrets(
            riot_api_key=os.environ["RIOT_API_KEY"],
            discord_application_id=os.environ["DISCORD_APPLICATION_ID"],
            discord_user_id=os.environ["DISCORD_USER_ID"],
            discord_bot_token=os.environ["DISCORD_BOT_TOKEN"],
        ),
        riot=RiotSettings(
            platform=riot["platform"],
            region=riot["region"],
            puuid=riot.get("puuid"),
            game_name=riot.get("game_name"),
            tag_line=riot.get("tag_line"),
            ranked_queue=riot["ranked_queue"],
            matches_for_kda=int(riot["matches_for_kda"]),
        ),
        discord=DiscordSettings(
            title_suffix=cfg["discord"]["title_suffix"],
            field_names=cfg["discord_field_names"],
        ),
        behavior=BehaviorSettings(
            update_mode=behavior.get("update_mode", "interval"),
            check_interval_seconds=int(behavior.get("check_interval_seconds", 120)),
            update_interval_seconds=int(behavior.get("update_interval_seconds", 600)),
            max_staleness_seconds=int(behavior.get("max_staleness_seconds", 3600)),
        ),
        icons=IconSettings(
            rank_base=cfg["icon_urls"]["rank_base"],
            role_base=cfg["icon_urls"]["role_base"],
            profile_icon_base=cfg["icon_urls"]["profile_icon_base"],
        ),
    )
