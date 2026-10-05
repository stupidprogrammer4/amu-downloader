# AMU Downloader

A standalone aiogram webhook bot with a Papilio API, MySQL persistence and
Papilio Tasks workers. Planning, concurrent file transfers and ordered Telegram
delivery have separate owners. Each completed transfer enters the delivery
queue immediately; collection positions determine the sending order. Files are
removed after delivery, with scheduled cleanup for inactive workspaces.

## Run

Requires Python 3.13 and Docker Compose v2. Copy `.env.example` to a private
`.env`, fill the credentials and copy `config.yml.sample` to `config.yml`.
The downloader uses its own database, Redis namespace and bot token.

```bash
docker compose up -d --build
docker compose exec -T bots python -m downloader_bot.webhooks
```

Expose only `/telegram/media` through HTTPS to the bot gateway on local port
18021. API port 18020 and `/internal/*` gateway routes must remain private.
The API and gateway expose `/health/live` for container health checks.

## Configuration

MySQL owns `media.policy/global`: quotas, provider routes, collection size,
concurrency, timeouts, disk limits and menu text. Seeds create missing records
without replacing edited values. Credentials and storage paths belong in private
runtime configuration. Collection limits reject oversized collections; they do
not silently truncate them. Uncertain Telegram sends are not automatically
repeated. `/exit` clears the selected mode without cancelling accepted jobs.

Provider access is evaluated for each request. Login challenges and unavailable
formats can prevent transfers. Spotify audio substitution is disabled; original
Spotify audio is not available in this version. Spotify is disabled in the
initial policy. YouTube transfers depend on accessible source formats and any
configured source API.

## Development

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r api/requirements-dev.lock -r bots/requirements.lock
.venv/bin/pip install --no-deps -e packages/contracts -e api -e bots
.venv/bin/ruff check api bots packages tests
.venv/bin/ruff format --check api bots packages tests
.venv/bin/pyright
.venv/bin/python -m pytest tests -q
```

Native integration tests require isolated `DOWNLOADER_TEST_DATABASE_URL` and
`DOWNLOADER_TEST_REDIS_URL`. They execute real MySQL, Redis, scheduler and worker
operations against controlled external HTTP and Telegram boundaries. FFmpeg
creates test media; these tests do not establish public provider availability.
The optional container network test requires `DOWNLOADER_BOT_TEST_IMAGE`.

Licensed under MIT.
