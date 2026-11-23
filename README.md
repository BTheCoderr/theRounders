# The Rounders

NBA and NFL predictive analytics: power rankings, pregame projections, and a public record of how those projections performed.

> **Security notice (November 2026):** Provider API keys were previously committed to this public repository. Removing them from the code does not revoke them, and they remain in Git history. Revoke and reissue the exposed Odds API, Tomorrow.io weather and MySportsFeeds credentials before relying on those accounts. Never commit credentials; use Netlify environment variables and the `.env.example` files.
>
> **Release status:** The web app and the iOS/Android app are implemented but not yet released to the App Store. Prediction performance has not been independently validated. Do not describe the predictions as profitable or proven.

## Repository layout

| Path | What it is |
| --- | --- |
| `native/` | Next.js 15 web app and API, deployed to Netlify (`netlify.toml` sets `native` as the base). Also holds the Netlify scheduled functions and Supabase migrations. See [native/README.md](native/README.md). |
| `mobile/` | Expo (SDK 54) React Native app for iOS and Android. It reads the deployed web API. See [mobile/README.md](mobile/README.md). |
| `.github/workflows/` | CI for `native/` and `mobile/`, the manual TestFlight workflow, and the scheduled Supabase health check. |

The legacy Python and Streamlit research code was removed in November 2026. The last commit that contains it is tagged `legacy-python-final`.

## Run locally

Web app and API:

```sh
cd native
npm install
cp .env.example .env.local   # fill in server-side values; never commit them
npm run dev
```

Mobile app:

```sh
cd mobile
npm ci --legacy-peer-deps
cp .env.example .env         # EXPO_PUBLIC_ROUNDERS_API_URL only; no secrets on the device
npx expo start
```

## Checks

```sh
cd native && npm run typecheck && node --experimental-strip-types --test tests/*.test.mjs && npm run build
cd mobile && npm run typecheck && node --experimental-strip-types --test tests/*.test.mjs
```

## Data and disclaimers

Historical results come from ESPN's public scoreboard endpoint, which is unofficial and carries no completeness guarantee or commercial-use license. Market prices are clearly labeled live or simulated. The product is for research and paper tracking only; it does not place wagers.
