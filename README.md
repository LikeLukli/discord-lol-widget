# discord-lol-widget

Shows my League of Legends stats on my Discord profile, using the
(experimental) app profile widget feature. Rank, LP, winrate, average KDA and
main role over the last 20 ranked games, plus the in-game profile icon.

It runs as a small loop: every couple of minutes it asks the Riot API for the
most recent match id (a single cheap request), and only when a new match shows
up does it fetch everything and PATCH the Discord profile. So the widget
updates a few minutes after a game ends instead of on a dumb timer — though
the dumb timer is still available as `update_mode: interval` if you want it.

Heads up: the widget API is an experimental Discord feature and undocumented,
so this whole thing can stop working whenever Discord feels like it.

## Setup

You need:

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- a Riot API key from https://developer.riotgames.com (note: dev keys expire
  after 24h, you'd need a personal/production key for anything long-running)
- a Discord application with the profile widget experiment set up, and its
  bot token

Then:

```
git clone <this repo>
cd discord-lol-widget
uv sync
cp .env.example .env                    # fill in your keys/ids
cp config.example.yaml config.yaml      # fill in your riot id, region etc.
uv run main.py
```

Both real files (`.env`, `config.yaml`) are gitignored.

## Config notes

- `riot.game_name` / `riot.tag_line` is your Riot ID (the `Name#TAG` thing).
  Alternatively set `riot.puuid` directly and skip the lookup.
- `riot.platform` is the server (`euw1`, `na1`, ...), `riot.region` the
  routing region (`europe`, `americas`, `asia`).
- `discord_field_names` has to match the field keys you defined in the
  Discord application's widget config, otherwise the values go nowhere.
- `behavior.max_staleness_seconds` forces a refresh every hour even without a
  new match, so stuff like a changed profile icon or dodge LP loss still shows
  up eventually. Set it to 0 to only ever update after matches.

Icons are hotlinked from [CommunityDragon](https://www.communitydragon.org/).
