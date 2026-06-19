# Daily Literature and SotA Update

Status: local Mac operating procedure.

CAPAS keeps market and literature positioning current through a daily local watch
run. The watchlist is not a novelty claim and not a CAPAS verdict. It is an
intake queue for human review.

## What runs daily

The daily job runs:

```bash
scripts/run_daily_sota_update.sh
```

That script:

1. queries Semantic Scholar and arXiv for CAPAS-relevant topics,
2. deduplicates candidates,
3. scores them for relevance to CAPAS positioning,
4. writes a dated JSON artifact under `outputs/sota_watch/`,
5. updates `docs/SOTA_DAILY_WATCH.md`,
6. runs `python3 capas.py validate` so the product remains green after the
   watch update.

Generated files:

- `outputs/sota_watch/YYYY-MM-DD.json`
- `docs/SOTA_DAILY_WATCH.md`
- `outputs/logs/sota-daily.out.log`
- `outputs/logs/sota-daily.err.log`

## Manual run

From the repo root:

```bash
chmod +x scripts/run_daily_sota_update.sh
scripts/run_daily_sota_update.sh
```

If you want a no-network smoke test:

```bash
python3 scripts/update_sota_watch.py --offline
```

Optional, but recommended for stable Semantic Scholar rate limits:

```bash
export SEMANTIC_SCHOLAR_API_KEY="..."
scripts/run_daily_sota_update.sh
```

Without an API key, the watcher still falls back to arXiv and records any
Semantic Scholar rate-limit response in the dated JSON artifact instead of
silently hiding it.

## Install daily macOS schedule

Copy the LaunchAgent:

```bash
cp ops/launchd/com.capas.sota-daily.plist ~/Library/LaunchAgents/com.capas.sota-daily.plist
```

Load it:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.capas.sota-daily.plist
```

Run it immediately once:

```bash
launchctl kickstart -k gui/$(id -u)/com.capas.sota-daily
```

Inspect status:

```bash
launchctl print gui/$(id -u)/com.capas.sota-daily
```

Unload it:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.capas.sota-daily.plist
```

## Promotion rule

A daily watch result is only promoted into durable docs such as
`docs/SOTA_POSITIONING.md` or `docs/GLOBAL_SOTA_MARKET_AUDIT.md` after a human
review records:

1. what the source occupies,
2. what CAPAS must not claim because of that source,
3. what defensible CAPAS gap remains,
4. source URL/DOI and retrieval date.

This keeps CAPAS fresh without turning search results into unverified marketing
claims.

## Recommended daily operating loop

1. Read `docs/SOTA_DAILY_WATCH.md`.
2. Pick 1-3 high-relevance candidates.
3. Open the source papers/products.
4. Promote only reviewed findings into the stable SOTA docs.
5. Commit the watch artifact and any promoted documentation changes.

## Explicit claim boundary

CAPAS will say:

> We maintain daily literature and market surveillance for CAPAS positioning,
> but we only promote reviewed sources into stable product claims.

CAPAS will not say:

> Every daily watch candidate has been validated or proves CAPAS novelty.
