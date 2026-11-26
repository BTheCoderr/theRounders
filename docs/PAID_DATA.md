# Paid odds and injury data

Everything in this branch is **off by default**. No paid request is made until the flags below are set, and no purchase has been made.

## Providers (checked 2026-11-24 against the providers' public pricing and terms; re-check before buying)

| Need | Provider and plan | Price | Why this plan |
|---|---|---|---|
| Live odds, all six sports | The Odds API, 20K credits | $30/mo | Our polling plan uses about 6.6k credits/month (3 credits per sport capture). Historical odds need a paid plan and cost 10x per call, so they are not used by the scheduled job. |
| NBA injuries + box scores (impact ratings) | BALLDONTLIE NBA GOAT | $39.99/mo | Injuries need All-Star or higher; box scores (minutes, plus-minus) need GOAT. A 7-day GOAT trial exists, so test with that first. |
| NFL injuries + QB season stats | BALLDONTLIE NFL All-Star | $9.99/mo | Player injuries and season stats are on All-Star. |

Licensing: both providers allow commercial display in our product. The Odds API forbids reselling the raw feed. BALLDONTLIE forbids building a substitute API, and its data should not be the only source for settling wagers. Neither requires attribution, but we show the source anyway.

## Environment variables (Netlify, server-side only; never commit values)

```
ODDS_INGEST_ENABLED=1
ODDS_API_KEY=...
ODDS_MONTHLY_CREDITS=20000        # the purchased plan
ODDS_BUDGET_FRACTION=0.85         # optional; month cap and provider-side reserve
ODDS_DAILY_FRACTION=0.06          # optional; daily cap
BALLDONTLIE_ENABLED=1
BALLDONTLIE_API_KEY=...
BALLDONTLIE_MONTHLY_REQUESTS=60000 # optional ceiling
```

Apply `native/supabase/migrations/012_rounders_odds_injuries.sql` before enabling either provider.

## What runs

- `rounders-odds`, every 15 min: the free `/events` call decides; `/odds` runs only for openers/updates (6h) or the closing window (≤45 min before start), within budget. Visitors read stored snapshots (`/api/markets`), so traffic never spends credits.
- `rounders-injuries`, hourly: NBA/NFL reports, logged with first-seen/last-seen times. Then v4 forecasts are written as **new timestamped rows** in `rounders_adjusted_forecasts`. Locked `rounders_predictions` rows are never changed.
- `rounders-impacts`, daily: NBA box scores to regressed plus-minus impacts. NFL uses a starting-QB prior.
- Grading (hourly) also grades v4 forecasts from the locked picks' finals.

## Evidence rules

- Injury history is not available from the provider, so **v4 is forward-test only** (`/api/performance` → `forward`, compared with power-v2 on the same games).
- `/api/market-analytics`: CLV vs the captured opening line, ATS vs the close, and Brier vs the market close. Uncaptured games are excluded.
- Backtests add walk-forward Platt calibration per sport and the `ensemble-w` challenger (PR #38 weights refit each week on earlier games only).
- No accuracy improvement is claimed until these reports show it on enough games.
