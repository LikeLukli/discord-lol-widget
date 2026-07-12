"""Main loop: fetch stats from Riot and push them to the Discord widget."""

from __future__ import annotations

import logging
import time

from lol_widget.config import Settings, load_settings
from lol_widget.discord.client import DiscordApiError, DiscordClient
from lol_widget.discord.payload import build_profile_payload
from lol_widget.riot.client import RiotApiError, RiotClient
from lol_widget.riot.stats import build_stats_bundle, queue_id_for

log = logging.getLogger("lol_widget")


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def _resolve_puuid(riot: RiotClient, settings: Settings) -> str:
    if settings.riot.puuid:
        return settings.riot.puuid
    if not (settings.riot.game_name and settings.riot.tag_line):
        raise RuntimeError(
            "Neither riot.puuid nor riot.game_name/tag_line is set in config.yaml."
        )
    return riot.resolve_puuid(settings.riot.game_name, settings.riot.tag_line)


def _update_widget(riot: RiotClient, discord: DiscordClient, settings: Settings, puuid: str) -> None:
    log.info("Getting stats from the Riot API...")
    stats = build_stats_bundle(riot, settings, puuid)
    log.info(
        "Rank=%s LP=%s WR=%s Level=%s Role=%s KDA=%s",
        stats.rank_text, stats.lp, stats.winrate_ranked,
        stats.account_level, stats.main_role, stats.avg_kda,
    )
    discord.update_profile(build_profile_payload(stats, settings.discord))


def _run_interval(riot: RiotClient, discord: DiscordClient, settings: Settings, puuid: str) -> None:
    interval = settings.behavior.update_interval_seconds
    log.info("Updating every %ss.", interval)
    while True:
        try:
            _update_widget(riot, discord, settings, puuid)
        except (RiotApiError, DiscordApiError) as e:
            log.error("%s", e)
        except Exception:  # noqa: BLE001 - keep the loop alive on unexpected errors
            log.exception("Unexpected error")
        time.sleep(interval)


def _run_on_new_match(riot: RiotClient, discord: DiscordClient, settings: Settings, puuid: str) -> None:
    behavior = settings.behavior
    queue_id = queue_id_for(settings.riot.ranked_queue)
    log.info(
        "Checking for new matches every %ss (forced refresh: %s).",
        behavior.check_interval_seconds,
        f"every {behavior.max_staleness_seconds}s" if behavior.max_staleness_seconds else "off",
    )

    last_match_id: str | None = None
    last_update: float | None = None

    while True:
        try:
            latest_match_id = riot.get_latest_match_id(puuid, queue_id)

            now = time.monotonic()
            stale = (
                behavior.max_staleness_seconds > 0
                and last_update is not None
                and now - last_update >= behavior.max_staleness_seconds
            )

            if last_update is None:
                reason = "startup"
            elif latest_match_id != last_match_id:
                reason = f"new match {latest_match_id}"
            elif stale:
                reason = "periodic refresh"
            else:
                reason = None

            if reason:
                log.info("Updating widget (%s).", reason)
                _update_widget(riot, discord, settings, puuid)
                last_match_id = latest_match_id
                last_update = time.monotonic()
        except (RiotApiError, DiscordApiError) as e:
            log.error("%s", e)
        except Exception:  # noqa: BLE001 - keep the loop alive on unexpected errors
            log.exception("Unexpected error")

        time.sleep(behavior.check_interval_seconds)


def run() -> None:
    _setup_logging()
    settings = load_settings()

    riot = RiotClient(
        api_key=settings.secrets.riot_api_key,
        platform=settings.riot.platform,
        region=settings.riot.region,
    )
    discord = DiscordClient(
        application_id=settings.secrets.discord_application_id,
        user_id=settings.secrets.discord_user_id,
        bot_token=settings.secrets.discord_bot_token,
    )

    log.info("Starting lol-widget (mode: %s, config: %s)",
             settings.behavior.update_mode, settings.config_path)
    puuid = _resolve_puuid(riot, settings)

    try:
        if settings.behavior.update_mode == "on_new_match":
            _run_on_new_match(riot, discord, settings, puuid)
        else:
            _run_interval(riot, discord, settings, puuid)
    except KeyboardInterrupt:
        log.info("Stopped.")
