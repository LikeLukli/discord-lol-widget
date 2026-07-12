"""Builds the identity profile payload for the Discord widget."""

from __future__ import annotations

from lol_widget.config import DiscordSettings
from lol_widget.riot.stats import StatsBundle

# Field types of the experimental identity profile API.
FIELD_TEXT = 1
FIELD_NUMBER = 2
FIELD_IMAGE = 3


def build_profile_payload(stats: StatsBundle, discord: DiscordSettings) -> dict:
    fields = discord.field_names
    dynamic = [
        {"type": FIELD_TEXT, "name": fields["title"], "value": f"{stats.display_name}{discord.title_suffix}"},
        {"type": FIELD_TEXT, "name": fields["rank"], "value": stats.rank_text},
        {"type": FIELD_NUMBER, "name": fields["lp"], "value": stats.lp},
        {"type": FIELD_TEXT, "name": fields["winrate_ranked"], "value": stats.winrate_ranked},
        {"type": FIELD_NUMBER, "name": fields["account_level"], "value": stats.account_level},
        {"type": FIELD_TEXT, "name": fields["main_role"], "value": stats.main_role},
        {"type": FIELD_TEXT, "name": fields["avg_kda"], "value": stats.avg_kda},
    ]

    if stats.rank_icon_url:
        dynamic.append(
            {"type": FIELD_IMAGE, "name": fields["rank_icon"], "value": {"url": stats.rank_icon_url}}
        )
    if stats.main_role_icon_url:
        dynamic.append(
            {"type": FIELD_IMAGE, "name": fields["main_role_icon"], "value": {"url": stats.main_role_icon_url}}
        )
    if stats.profile_icon_url:
        dynamic.append(
            {"type": FIELD_IMAGE, "name": fields["profile_icon"], "value": {"url": stats.profile_icon_url}}
        )

    return {"data": {"dynamic": dynamic}}
