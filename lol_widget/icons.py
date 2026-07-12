"""Maps Riot tiers, roles, and profile icon IDs to CommunityDragon image URLs."""

from __future__ import annotations

from lol_widget.config import IconSettings

_RANK_FILES = {
    "IRON": "iron.png",
    "BRONZE": "bronze.png",
    "SILVER": "silver.png",
    "GOLD": "gold.png",
    "PLATINUM": "platinum.png",
    "EMERALD": "emerald.svg",  # no PNG for Emerald :(
    "DIAMOND": "diamond.png",
    "MASTER": "master.png",
    "GRANDMASTER": "grandmaster.png",
    "CHALLENGER": "challenger.png",
}

_ROLE_FILES = {
    "TOP": "icon-position-top.png",
    "JUNGLE": "icon-position-jungle.png",
    "MIDDLE": "icon-position-middle.png",
    "BOTTOM": "icon-position-bottom.png",
    "UTILITY": "icon-position-utility.png",
}


def rank_icon_url(icons: IconSettings, tier: str) -> str | None:
    filename = _RANK_FILES.get(tier)
    return f"{icons.rank_base}/{filename}" if filename else None


def role_icon_url(icons: IconSettings, position: str) -> str | None:
    filename = _ROLE_FILES.get(position)
    return f"{icons.role_base}/{filename}" if filename else None


def profile_icon_url(icons: IconSettings, icon_id: int) -> str:
    return f"{icons.profile_icon_base}/{icon_id}.jpg"
