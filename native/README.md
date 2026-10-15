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
