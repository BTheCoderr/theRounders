# therounders native mobile (Expo)

This is an actual Expo React Native iOS/Android client, separate from the legacy Streamlit analytics and the responsive Next.js service in \`native/\`.

## Available now

- NBA / NFL / NHL / MLB market boards with same-line multi-book comparisons
- Explicitly labeled demo/fallback or live data
- Price gaps based on book-to-book odds, not fabricated steam/RLM signals
- Read-only matchup model estimates from Rounders API, labeled with source/fallback status
- On-device paper tickets, result marking and bankroll summaries; no real transactions

## Build prerequisites

From \`mobile/\`:

\`\`\`sh
npm ci --legacy-peer-deps
cp .env.example .env
# Set EXPO_PUBLIC_ROUNDERS_API_URL to the deployed HTTPS Rounders API origin.
npx expo start
\`\`\`

Run \`npm run typecheck\` and \`npx expo export --platform ios\` or \`--platform android\` first. The GitHub CI workflow validates both exports.

Only \`EXPO_PUBLIC_ROUNDERS_API_URL\` belongs on the device. Store provider credentials on the server. Without a reachable API, use visibly simulated demo mode. **Never call those prices live.**

The Expo project is already linked to `@bferrell514/therounders`. The iOS bundle identifier is `com.bthecoderr.therounders`; confirm that it belongs to the intended Apple Developer account. The approved app icon must still be committed before a signed build. No TestFlight upload or physical-device QA has been completed. No wagers can be placed by this app.


## Preparing the iOS TestFlight build

The iOS and Android React Native source is in this `mobile/` directory, not `native/` (which holds the web dashboard). GitHub Actions verifies the JavaScript export but **does not** create an Apple-signed .ipa. EAS project `@bferrell514/therounders` (`40f4305a-ef4e-48bf-aedf-f16068e20791`) is already linked. A signed build still has to be requested explicitly.

1. Stay on Expo account `bferrell514`. Do not run `eas init` again unless `expo.extra.eas.projectId` is removed. Confirm the bundle identifier `com.bthecoderr.therounders` belongs to the intended Apple Developer account before generating certificates. It is not yet registered with Expo Apple credentials, and no public App Store record exists for it.
2. The production Rounders API origin is `https://therounders.netlify.app`. It is set on the production EAS build profile as `EXPO_PUBLIC_ROUNDERS_API_URL`. Only this public origin can go in a client-side `EXPO_PUBLIC_` variable; keep sportsbook provider keys on the backend. The production EAS profile is explicitly mapped to the production environment. The deployed feed is still the controlled demo provider until a live odds key is configured on the server, and the app must keep that state labeled simulated.
3. Configure iOS distribution credentials and App Store Connect API access in your own Expo/Apple accounts (`npx eas-cli credentials --platform ios`). Check that the correct app exists in App Store Connect and supply its numeric `ascAppId` in `eas.json > submit.production.ios` before attempting a noninteractive upload.
4. Use only the recovered approved sports-R primary artwork as the iOS/Android icon. Its verified SHA-256 is `377fa28d0df652926debe87146a186682ed99df8aecb4741dc8102c8ed3449d4`. The `therounders-ios-ready-to-push.zip` installation package includes a verified installer that creates `mobile/assets/icon.png`, sets `expo.icon` to `./assets/icon.png`, runs `npm run preflight:ios`, then commits and pushes *only* these two paths from a clean up-to-date `main`. Never add an icon path without the binary. Keep the analytics-R design as alternate marketing artwork. Take real-device screenshots and confirm the market-feed mode is accurately labeled.
5. On GitHub, add `EXPO_TOKEN` under repository **Settings → Secrets and variables → Actions**. Do not commit credentials or the token.
6. Run **Actions → therounders iOS TestFlight (manual) → Run workflow**. Leave `submit_to_testflight` unchecked to create only an Apple-signed store build. Choose it only when TestFlight submission is explicitly desired and the App Store Connect API key is configured.

Alternatively, once setup is complete, run locally from `mobile/`:
```sh
npx eas-cli build --platform ios --profile production
npx eas-cli submit --platform ios --profile production
```

A passing Expo JavaScript export is **not** evidence that an .ipa was signed, a tester installed it, or Apple accepted it. No real wagering is included.

## Release preflight

Run `npm run preflight:ios` after linking EAS and adding the approved icon. The script rejects a missing project ID, invalid bundle identifier, missing/transparent/wrong-sized PNG, or wrong production build environment. Run `node scripts/release-preflight.mjs --submit` before automatic TestFlight submission; that mode also requires the numeric App Store Connect `ascAppId` in `eas.json`.

The manually dispatched TestFlight workflow now runs the same checks before installing dependencies and starting a paid/signed EAS build. These are static release guards, not evidence of App Store approval, live odds correctness, or physical-device QA.

The full-resolution approved 1024x1024 primary art must be committed as the actual PNG file, not just referenced in `app.json`. Keep the separate alternate art out of the app icon. Do not run `eas init` again, because the correct Expo project is already linked. No EAS build or submission should be launched while signing, `ascAppId`, or iPhone QA is outstanding.

## Rounders AI matchup analyst

The Board now includes **Ask Rounders AI** for each matchup, and a dedicated **Rounders AI** tab offers a bounded question input and explanations from the backend `POST /api/ai/matchup` endpoint. It shows **AI EXPLANATION** only when the server actually calls a generative model. Otherwise the same workflow returns **MODEL SUMMARY · GENERATIVE AI OFF**, with modeled scores, favored team, provenance and explicit limits. Every result identifies external versus simulated training data; nothing here is guaranteed, backtested, or a verified injury/news feed.

The AI key is never in Expo or GitHub. Configure `OPENAI_API_KEY` and `ROUNDERS_AI_ENABLED` *only* server-side after durable production rate limiting / provider budgets exist. Until then, the statistical explanation works without keys and no LLM calls are made. Expo's configured `EXPO_PUBLIC_ROUNDERS_API_URL` must point at the updated deployed backend for these screens to work on a device.


## Power Index preview

The new Power Index tab reads `GET /api/power-rankings` for NBA, NFL, NHL and MLB, shows the ranked teams with schedule-opponent strength, win-loss records, point-margin and recent form, and displays a chronological holdout MAE comparison. The current backend's ESPN history coverage is not guaranteed complete; sparse data and simulated fallback are prominently labeled. These are *experimental* power rankings inspired by the classic least-squares method, not Kenneth Massey's official ratings, nor trained/calibrated probability estimates. Switching sports cancels stale ranking displays. A live provider or full-season archive is needed before marketing them as robust league standings.
