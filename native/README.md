# The Rounders Native

This directory is the Next.js web app and API for The Rounders. It is the only server-side code in the repository; the legacy Python/Streamlit research system was removed (see the `legacy-python-final` tag).

## Principles

- Mobile-first product UI
- Provider adapters instead of sportsbook-specific UI code
- Every datum is labeled live, model, or simulated
- Paper mode is the safe default
- No provider secret is exposed to the browser

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


## Massey research report implementation (October 2026)

The user-supplied `Modernizing Massey Ratings for therounders: Rounders Power Index v2` recommends keeping least-squares schedule adjustment while testing learned home advantage, pure recency weights, robust margin loss, prior-season shrinkage, context, and properly calibrated probabilities against locked chronological holdouts.

### Implemented research-only slice

- `lib/researchRpi.ts` fits a **separate** `rounders-research-v2.1` experimental model, using completed games before the cutoff, Huber IRLS, exponential half-life recency, joint league home advantage estimation with shrinkage, regularization and optional previous-season prior ratings. Default priors and Huber thresholds are placeholders, NOT tuned optimums. No extra key required; it does not replace production ratings or emit uncalibrated winning percentages.
- `lib/walkForward.ts` includes the experimental model as the **fifth** weekly expanding-origin comparator on identical held-out games alongside home baseline, basic Massey ridge, Elo and Power Index v2.
- `lib/researchDataQuality.ts` and `GET /api/data-quality?sport=NBA` surface approximate league-season game counts, expected team labels, and missing-season risks. Model Lab displays these warnings even when a stored weekly comparison exists. Candidate seasons are **not certified complete** based on a count alone.

### Data audit findings and limitations

At the initial implementation audit, the Supabase archive included 2024–2026 calendar-dated records with fewer than five usable complete seasons per league. Team name counts included labels beyond normal NBA/NHL roster-size expectations, indicating a need to check for preseason/all-star exhibitions, renamed teams and aliases; **do not interpret raw archive rows as verified full-season regular-season games**. The estimated game-count thresholds are not a replacement for comparing against an authoritative game schedule.

### Next implementation gates (not yet delivered)

1. Canonical external provider event IDs and team IDs, game stage (regular/postseason/preseason), verified completed timestamp; reconcile actual schedules and correct provider licensing.
2. Obtain and audit at least five complete historical seasons per league, preferably 8–10.
3. Sport-specific parameter tuning only on historical development/validation seasons; compare raw, clipped and Huber margins, estimated home models and preseason priors with ablations.
4. Freeze each out-of-sample pregame forecast and independently train a logistic calibrator on **past frozen** forecasts. Publish Brier score, log loss, MAE, RMSE and calibration plots with reliability sample counts and intervals.
5. Add offense/defense and rest/context only when they improve truly unseen-season performance; investigate team-level uncertainty and model change logs.
6. Shadow test, audit dataset version and code commit, verify rollbacks, then consider replacing the live model only after passing documented objective release criteria.

**Important:** The original website's current Massey Ratings are more involved than classic least squares; our `massey-ridge` comparator is a mathematical reference, not Kenneth Massey's proprietary production ratings. We cannot claim to outperform the official site without a matched independent evaluation.


## Regular-season historical archive integrity (revision 2, October 2026)

Migration `007_regular_season_provider_ids.sql` adds stable ESPN event/team IDs, provider season, season phase, verification timestamp, monthly ingestion revision and a private team registry. It is **non-destructive**: the previous 2,472 score-only game records are intentionally preserved as `season_phase=unknown`. They must not be silently rebranded as regular-season observations.

The new `lib/results/espnArchive.ts` parser accepts **only** completed games explicitly marked as regular season (`season.type=2`) with valid provider event/team identifiers, final integer scores and event date. It rejects unknown phase or malformed IDs for month-completeness purposes; known preseason, postseason and exhibition games are excluded. Data-source metadata is not assumed to prove a licensing right or a complete league schedule. The original display names remain on game rows for auditing; stable provider team IDs resolve to a single current canonical label in the private `rounders_team_registry`.

`refreshHistoricalArchive()` uses a **73-month** (~six-year) rolling ingestion window and reprocesses revision-0 months automatically to revision-2, one missing historical month per league per three-hour scheduled invocation, plus a stale current month. The updated importer upserts verified regular-season rows and reconciles legacy rows with the same stable hashed identity where possible; other legacy rows remain `unknown`. Failure to validate a month leaves its receipt at its previous revision so it is eligible for retry. This is a *slow, safe backfill*, not a promise of complete multi-season coverage.

Research-only `getVerifiedResearchGames()` reads **exclusively regular-season, provider-ID-backed records**, canonicalizes names by provider team ID, and does not fall back to unclassified or simulated results. Daily `saveComparison()` and `/api/data-quality` now use this verified subset. `readComparison()` excludes historical comparison rows computed from the unclassified feed, so the public Model Lab must show "waiting" until a revised verified scorecard is stored. Existing pre-release ratings and matchup projections still use their previous preview source path and are not silently replaced by the research engine.

Validation requirements before promotion: reconcile each provider event against authoritative regular-season schedules; identify stable franchise renames; verify all 30/32 expected clubs, completed status and season boundaries; obtain usage rights for ongoing data storage and redistribution; collect at least five complete seasons per sport; and measure locked-test performance with a reproducible data revision. Expected league game counts in the data audit are approximate, not an audit of every schedule fixture. The `source_event_id` synthetic legacy ID remains an internal conflict key, while `provider_event_id` is preserved separately.

For unit tests: `node --experimental-strip-types --test tests/regularArchive.test.mjs`. To validate the initial backfill, query `public.rounders_history_months` for `ingestion_revision=2` and `public.rounders_games` for `season_phase='regular'`, then ensure `public.rounders_model_comparisons.data_source` reports `Rounders verified regular-season ESPN archive`. The server role alone can read/write these tables; do not expose database service credentials in clients or GitHub.


## Import scheduling isolation (October 2026)

The four regular-season history import functions now run **only one month per invocation**, on staggered three-hour UTC intervals (NBA :00, NFL :15, NHL :30, MLB :45). Model computation was removed from the same 30-second invocation to avoid a slow walk-forward comparison preventing a completed game import receipt. Four independent daily evaluation functions run at 14:00/14:15/14:30/14:45 UTC. All eight schedules are specified both in source and in root `netlify.toml`, so future releases can statically verify registration. These functions use existing Supabase service-role credentials on Netlify, not mobile secrets.

The initial six-year backfill may take weeks at one old month per three-hour run, depending on provider behavior, empty months, Netlify scheduling and source coverage. There is no assertion of complete history based only on having a month receipt. The automated import watch observes `season_phase='regular'`, `provider_event_id` and `ingestion_revision>=2`; successful deployment does not prove scheduled execution. Check Netlify Functions dashboard for each registered name, and use its **Run now** control if immediate first invocation is needed. If no new verified rows appear, investigate provider event shape and function execution logs before tuning models.


## NBA/NFL prediction engine (engine-1, November 2026)

The engine lives in `lib/engine/` and is the only path for stored predictions. NBA and NFL only; MLB/NHL history keeps importing but is not modeled.

**Models.** Candidates: `rounders-v1` (the model customers have been shown), `power-v2`, `rpi-v2.1`. Benchmarks: home-advantage baseline, Elo, least-squares ridge. Every model produces a home-minus-away margin. Totals and projected scores come from one shared model, `totals-v1` (recency-weighted ridge offense/defense). Win probability is `Φ(margin / σ)` with fixed σ (NBA 12, NFL 13.5); it is an assumption whose calibration is measured, not claimed.

**Champion.** `ROUNDERS_CHAMPION_NBA` / `ROUNDERS_CHAMPION_NFL` (default `rounders-v1`). Nothing switches automatically. The daily backtest runs a promotion gate (`lib/engine/promotion.ts`): a challenger must beat the champion on the same out-of-sample games, by more than two standard errors of the paired margin-error difference, with a Brier score no worse, over at least 600 NBA / 250 NFL games spanning two seasons. A passing gate is shown in `/api/performance`; promotion is then a deliberate env change and redeploy.

**Snapshots.** `rounders-predict-nba` (daily 15:20 UTC, next ~26 h) and `rounders-predict-nfl` (daily 15:25 UTC; the whole week on Tuesdays, two days otherwise) store one immutable row per game and candidate model in `rounders_predictions` (migration 008). Each row carries the model version, prediction time, training cutoff, projected winner, home win probability, projected scores, spread and total, and a consensus market line only when the odds provider is live. A database trigger blocks edits to prediction columns and a check constraint requires `predicted_at < starts_at`.

**Grading.** `rounders-grade` (every 3 h at :50) grades games that started 3+ hours ago from the verified archive, falling back to the ESPN scoreboard, matching by event and team IDs. Games with no result after 7 days are marked `void`.

**Backtests.** `rounders-backtest-nba` / `-nfl` (daily 13:05 / 13:20 UTC) run a weekly walk-forward over the verified regular-season archive (104 NBA weeks, 156 NFL weeks): each Monday every model is refit on earlier games only and predicts that week. Results and gate decisions go to `rounders_backtests`. Locally a synthetic 6,900-game NBA history takes about 9 s; check function durations after deploy against Netlify's 30 s scheduled-function limit.

**APIs.** `GET /api/predictions?sport=NBA|NFL` serves the champion's stored predictions. `GET /api/performance?sport=NBA|NFL` reports live graded results (accuracy, Brier, log loss, calibration, margin and total error, ATS/over-under only where a live line was captured) separately from backtest results.

## NBA/NFL web experience (November 2026)

The home page is NBA/NFL only, with one sport switch shared by every section: stored predictions (daily NBA, weekly NFL) with grounded "Explain this pick", the Power Index (verified regular-season archive for NBA/NFL), the free public track record (`/api/performance`), the line shop, price gaps and the paper bankroll. The browser-only "Model Scorecard" and the old Model Lab were removed: the track record now comes from server-stored, graded predictions. Model numbers appear next to market prices only when the prices are live and a stored prediction exists for that real game. `/api/ratings` remains for older clients but is no longer used by the web or mobile apps. `/api/markets` is cached per sport (45 s in memory, 30 s at the CDN) so visitors cannot drain the odds provider's quota.

## Plans and billing (Stripe TEST MODE)

Plans live in `lib/billing/plans.ts`: **Free** (projected winners and win probabilities, Power Index, the full public track record, model explanations, line shop, paper bankroll), **Rounders Pro** at a proposed $19.99/month (adds projected spreads, totals and scores, generative matchup analysis when enabled, CSV export of graded predictions), and **Rounders Edge** at a proposed $39.99/month (adds model-versus-live-market lines and every candidate model's predictions side by side). Gating is server-side in `/api/predictions`, `/api/predictions/export` and `/api/ai/matchup`; any failure resolves to Free.

Test mode is enforced three ways: `stripeKey()` refuses any key that is not `sk_test_`/`rk_test_`; the webhook rejects `livemode` events and subscriptions; migration `009_rounders_billing.sql` has `check (livemode = false)` on subscriptions and events.

Flow: the signed-in user (Supabase magic link) calls `POST /api/billing/checkout {plan}` → Stripe Checkout. `POST /api/billing/webhook` verifies the signature, re-reads the subscription from Stripe (so retries and out-of-order events converge) and upserts `rounders_subscriptions`. Plan changes, card updates and cancellation go through `POST /api/billing/portal`. A cancellation keeps access until the paid period ends; `past_due` keeps access until the period ends; `canceled`, `unpaid`, `incomplete` and `paused` fall back to Free.

Test-mode setup (Stripe Dashboard with **Test mode** on):
1. Products → create "Rounders Pro" ($19.99 monthly) and "Rounders Edge" ($39.99 monthly); copy each price ID into `STRIPE_PRICE_PRO` / `STRIPE_PRICE_EDGE`.
2. Developers → API keys → copy the test secret key into `STRIPE_SECRET_KEY` (Netlify, server scope only).
3. Developers → Webhooks → add endpoint `https://therounders.netlify.app/api/billing/webhook` with events `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`; copy the signing secret into `STRIPE_WEBHOOK_SECRET`.
4. Settings → Billing → Customer portal: allow switching between the two prices, payment-method updates and cancellation at period end.
5. Apply migration 009. Pay with test card `4242 4242 4242 4242`.

The iOS app has no purchases: any paid feature unlocked inside an iOS app must use Apple In-App Purchase, so the app shows Free-tier content and points to the website.
