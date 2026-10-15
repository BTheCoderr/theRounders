# The Rounders Native

This directory is the controlled product shell replacing Streamlit as the primary user experience. The legacy Python analytics remain available while functionality moves behind explicit APIs.

## Principles

- Mobile-first product UI
- Provider adapters instead of sportsbook-specific UI code
- Every datum is labeled live, model, or simulated
- Paper mode is the safe default
- No provider secret is exposed to the browser
- Streamlit can remain an internal analytics/admin surface during migration

## Local run

1. cd native
2. npm install
3. npm run dev

The starter market endpoint intentionally returns simulated data until a live provider adapter is configured.


## Release readiness (October 2026)

The `native/` folder currently contains a responsive **Next.js web application**, not an Expo/React Native iOS/Android application. Do not describe it as a signed App Store build. Its mobile layouts can be reused for a future native client.

The Line Shop compares quotes only when the event, market, side, and point line match. Price differences are not evidence of steam or reverse-line movement. Those indicators remain unavailable until a verified time-series feed exists. Live versus simulated sources are visible, and the interface is paper-only.

The link-based account view is not yet synced to paper bets; personal paper history stays in the browser. Do not promise multi-device sync until authenticated storage and RLS are implemented.

Review the `native/tests/` checks and run `npm run typecheck` plus `npm run build` before merging to the production branch.

## Grounded Rounders AI (opt-in)

`POST /api/ai/matchup` takes a JSON body such as
`{"sport":"NBA","away":"New York Knicks","home":"Boston Celtics","question":"Why does the model favor Boston?"}`.
The server validates the request, builds a fresh statistical projection from completed-game results (or *clearly labeled* controlled simulated fallback), and returns both a readable analysis and structured evidence. The iOS/Android app includes an **Ask Rounders AI** tab and a button on each matchup.

The endpoint is available in **model-summary** mode without any paid API key. Only when both server-side environment variables `OPENAI_API_KEY` and `ROUNDERS_AI_ENABLED=true` are configured will it call the OpenAI Responses API with `store:false` and a small text model (`ROUNDERS_AI_MODEL`, default `gpt-4.1-mini`). Never prefix either variable with `NEXT_PUBLIC_` or `EXPO_PUBLIC_`. The response explicitly reports `mode:"ai"` versus `mode:"model-summary"`, so the app never disguises model summaries as generated AI.

**Production security prerequisite:** The per-instance 8-request/15-minute guard helps with accidental bursts but is NOT a distributed rate limit across Netlify serverless invocations and cannot enforce a spend cap. Leave `ROUNDERS_AI_ENABLED` unset in public production until a durable shared quota / authentication limit and an upstream provider budget are established. Avoid sending personal details in questions, and keep API keys out of source control. The AI is grounded commentary, not a trained/validated predictive model, and the old statistical confidence metric is only a heuristic. The endpoint never promises guaranteed winners or verified injury/lineup/news information.

Run `node --experimental-strip-types --test tests/*.test.mjs` to check simulated provenance, missing-data disclosures, and response parsing. No provider credentials are necessary for those tests.


## Rounders Power Index v2 preview

`GET /api/power-rankings?sport=NBA|NFL|NHL|MLB` returns power rankings, opponent-average strength, game counts and W-L-T records, history source, sample completeness flag, and a preliminary chronological holdout MAE versus a home-advantage-only baseline.

The experimental `rounders-power-v2-preview` is **Massey-inspired, not official Massey Ratings**. It forms the weighted graph normal equations from completed game score differences and solves them with diagonally preconditioned conjugate gradients. Design choices include recency weighting (half-life per sport), regularization to cope with sparse/disconnected league schedules, bounded point margins for diminishing returns, and a fixed league home-advantage parameter. Those parameters are *not yet tuned against held-out seasons*. Ratings are relative **point margins**, not calibrated win probabilities or confidence percentages. These previews must not be advertised as independently validated predictions.

`holdoutMarginEvaluation` splits eligible completed games chronologically 70% training and 30% held-out, with no retraining on held-out results. It reports MAE for both v2 and a constant home-advantage baseline when at least five held-out games had known teams. A single chronological split is only diagnostic, not proven superiority. Future work: multi-season licensed or reputable historical dataset, rolling-origin backtests, strictly separate tuning and test windows, calibration, team identity mapping, publishing complete methodology.

Coverage warnings are required because the current ESPN scoreboard adapter is not a verified full-season historical feed. Results may be sparse, and `controlled-demo` fallback rankings must always say **SIMULATED**. The web and mobile clients must never treat a ranking as a betting recommendation.

Local tests: `node --experimental-strip-types --test tests/*.test.mjs`.


## Supabase history + AI production preparation

The existing project **The-Rounders** (`ykvsjnvpgdxsekqdhivz`) is reused. The Netlify production environment already points at this project via `NEXT_PUBLIC_SUPABASE_URL` and has a server-side `SUPABASE_SERVICE_ROLE_KEY`; no new Supabase project or extra database key is needed.

Apply the migrations under `native/supabase/migrations/` in ascending order. The new `003_rounders_history_ai_quota.sql` and `004_rounders_model_runs.sql` add:

- `rounders_games`: deduplicated, timestamped final scores by league and provider; no public reads or writes.
- `rounders_ingestion_runs`: per-league success/failure and row-count history.
- `rounders_model_runs`: dated MAE and baseline comparison for each sport.
- `rounders_ai_quota` and restricted service-role `rounders_claim_ai_quota` RPC: a shared, transactional counter. Maximum 100 billable AI requests globally each UTC day and 8 per hashed visitor every 15-minute window. A failed or inaccessible database always disables LLM spending while still returning non-AI model analysis.

Four staggered Netlify Scheduled Functions (`rounders-history-nba`, `rounders-history-nfl`, `rounders-history-nhl`, `rounders-history-mlb`) run independently every three hours on *published deployments*. Each invocation handles just one league, imports available completed games, and persists that league's model scorecards. Netlify's scheduled execution limit is 30 seconds, so all four leagues must never run sequentially inside the same invocation. It uses existing backend Supabase credentials and does **not** need a separate sports-results key. ESPN's annual scoreboard request is **not guaranteed to supply complete multi-season history**; importing verified comprehensive archives or a licensed history feed is still a future improvement. New tables start empty until the scheduled import runs; do not call simulated fallbacks real rankings.

The ratings API, Power Index API and Rounders AI endpoint prefer 10+ games from the stored database, fall back to ESPN completed results if the archive is too small/unavailable, then to clearly labeled simulated fixtures if both fail. There is no client-accessible privileged data mutation route.

### What to provide later

- `OPENAI_API_KEY`: create an OpenAI API project key and set it as a **secret** on the Netlify therounders site, never in mobile, source code or chat. Server-side `ROUNDERS_AI_ENABLED=true` and `ROUNDERS_AI_MODEL=gpt-4.1-mini` switch on billable commentary only when the key exists and the shared DB quota grants an allocation. Also set an OpenAI project-level budget and alerts.
- `ODDS_API_KEY`: optional server-only The Odds API key to replace simulated sportsbook quotes. Independent of the ESPN final-score archive.

The mobile production client already targets `https://therounders.netlify.app`, so it does not need any server secrets. Verify historical import receipts and quotas after the first run; do not claim full-season historical coverage until validated. An Apple-signed build, real device QA, and TestFlight remain separate from server readiness.

## Historical backfill and Model Lab (in progress)

A completed month scoreboard endpoint (`dates=YYYYMM`) powers a resumable 25-month rolling archive. Migration `006_rounders_history_months.sql` records which months have been imported. Each league's scheduled invocation fetches up to one older unprocessed month, the current month when stale, and previous month during its first five days. A failed month is retried; empty offseason months are recorded as empty instead of mistaken for missing data. Month snapshots are not a guarantee of complete league coverage, and source freshness should still be audited. Scheduled functions run on published production deployments, not on GitHub CI.

The new `native/lib/walkForward.ts` has four fixed untuned comparators: home-advantage-only, equal-weight ridge Massey-style, Elo margin, and Rounders Power Index v2. Every Monday-origin model fits only earlier games and predicts that week's fixtures as a sealed holdout. All models are evaluated on exactly the same matchups. The model lab reports MAE, winner accuracy, weeks, and sample years. For a meaningful comparison require at least 25 eligible games over four weeks; a single-year test does not establish overall superiority. Scores are recorded to RLS-protected `rounders_model_comparisons` (migration 005) and served read-only via `/api/model-comparison?sport=NBA` without exposing database secrets.

**No keys required** for historical game ingestion or model comparison. Only optional `OPENAI_API_KEY` for billable AI explanations and `ODDS_API_KEY` for sportsbook feeds remain. During first deployment the archive, monthly import tracking, and model comparisons will remain empty until the scheduled importer runs. Without a complete licensed/verified historical dataset, these are preview analytics, not proven better than Massey or Elo.


### Scheduled ingestion operations

The function directory is fixed at `native/netlify/functions` relative to the Netlify base `native` (configured in root `netlify.toml`). NBA runs at minute 0, NFL at minute 15, NHL at minute 30 and MLB at minute 45 of every three-hour window, UTC. Each bounded run imports at most one missing historical month and the current month when stale (plus the previous month near month turnover). With 24 historical months and no prior data, filling the backlog can take around three days and depends on the external scoreboard returning usable history. Scheduled Netlify functions cannot be invoked directly by a public URL; monitor `rounders_ingestion_runs`, `rounders_history_months`, `rounders_games` and `rounders_model_comparisons` after the next production schedule. A successful GitHub build or Netlify deployment does *not* establish that the scheduled job executed or imported games. No model result should be promoted as verified until the archive is populated.
