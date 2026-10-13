# Native Rounders architecture

The Streamlit application remains a legacy/internal analytics surface while the product migrates to a first-party application.

## Product surfaces

- Live Board: normalized odds from provider adapters
- Line Shop: best-price comparison
- Sharp Signals: movement/model signals with source and timestamp
- Paper Bankroll: positions, results, CLV and analytics
- Admin/Internal: existing Python research tools

## Architecture

The new `web/` application owns the user experience. Existing Python analytics remain usable while APIs are extracted behind stable contracts. Data providers must be replaceable adapters rather than UI dependencies.

No sportsbook execution is performed by the application. Paper tracking is the default product mode.

## Migration sequence

1. Native shell and responsive design
2. Read-only API contracts around existing Python analytics
3. Persistent storage and user workspaces
4. Live board and line-shopping UI
5. Signals with explicit provenance and freshness
6. Paper bankroll and analytics
7. Notifications and mobile client
