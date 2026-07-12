"""Aggregates Riot API data into the stats shown on the widget."""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass

from lol_widget import icons
from lol_widget.config import Settings
from lol_widget.riot.client import QUEUE_IDS, RiotClient

# Delay between match detail requests to stay under the Riot rate limits.
MATCH_FETCH_DELAY_SECONDS = 1.2


@dataclass
class StatsBundle:
    display_name: str
    rank_text: str
    rank_icon_url: str | None
    lp: int
    winrate_ranked: str
    account_level: int
    main_role: str
    main_role_icon_url: str | None
    avg_kda: str
    profile_icon_url: str | None


def format_rank(entry: dict | None, settings: Settings) -> tuple[str, str | None, int, str]:
    """Returns (rank_text, icon_url, lp, winrate) for a league entry."""
    if entry is None:
        return "Unranked", None, 0, "0%"

    tier = entry["tier"]  # e.g. "GOLD"
    rank = entry["rank"]  # e.g. "II"
    lp = entry["leaguePoints"]
    wins = entry["wins"]
    losses = entry["losses"]
    total = wins + losses
    winrate = f"{round(100 * wins / total)}%" if total else "0%"

    if tier in ("MASTER", "GRANDMASTER", "CHALLENGER"):
        rank_text = tier.capitalize()
    else:
        rank_text = f"{tier.capitalize()} {rank}"

    return rank_text, icons.rank_icon_url(settings.icons, tier), lp, winrate


def compute_kda_and_role(
    client: RiotClient, settings: Settings, puuid: str, match_ids: list[str]
) -> tuple[str, str, str | None]:
    """Returns (avg_kda, role_display, role_icon_url) over the given matches."""
    kills = deaths = assists = 0
    role_counter: Counter[str] = Counter()

    for match_id in match_ids:
        match = client.get_match(match_id)
        participant = next(
            p for p in match["info"]["participants"] if p["puuid"] == puuid
        )
        kills += participant["kills"]
        deaths += participant["deaths"]
        assists += participant["assists"]

        position = participant.get("teamPosition") or "UNKNOWN"
        if position != "UNKNOWN":
            role_counter[position] += 1

        time.sleep(MATCH_FETCH_DELAY_SECONDS)

    n = max(len(match_ids), 1)
    avg_kda = f"{kills / n:.1f}/{deaths / n:.1f}/{assists / n:.1f}"

    main_role = role_counter.most_common(1)[0][0] if role_counter else "UNKNOWN"
    role_display = main_role.title() if main_role != "UNKNOWN" else "Unknown"

    return avg_kda, role_display, icons.role_icon_url(settings.icons, main_role)


def queue_id_for(ranked_queue: str) -> int:
    return QUEUE_IDS.get(ranked_queue, QUEUE_IDS["RANKED_SOLO_5x5"])


def build_stats_bundle(client: RiotClient, settings: Settings, puuid: str) -> StatsBundle:
    summoner = client.get_summoner(puuid)
    entries = client.get_league_entries(puuid)

    ranked_entry = next(
        (e for e in entries if e["queueType"] == settings.riot.ranked_queue), None
    )
    rank_text, rank_icon, lp, winrate = format_rank(ranked_entry, settings)

    match_ids = client.get_recent_match_ids(
        puuid,
        count=settings.riot.matches_for_kda,
        queue_id=queue_id_for(settings.riot.ranked_queue),
    )
    avg_kda, main_role, role_icon = compute_kda_and_role(client, settings, puuid, match_ids)

    display_name = settings.riot.game_name or summoner.get("name") or "Summoner"

    return StatsBundle(
        display_name=display_name,
        rank_text=rank_text,
        rank_icon_url=rank_icon,
        lp=lp,
        winrate_ranked=winrate,
        account_level=summoner["summonerLevel"],
        main_role=main_role,
        main_role_icon_url=role_icon,
        avg_kda=avg_kda,
        profile_icon_url=icons.profile_icon_url(settings.icons, summoner["profileIconId"]),
    )
