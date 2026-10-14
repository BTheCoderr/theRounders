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

The App Store package IDs in \`app.json\` are provisional until confirmed in Apple and Google developer accounts. No icons/signed builds/TestFlight are included yet. EAS account linking, device QA and store assets are still required. No wagers can be placed by this app.


## Preparing the iOS TestFlight build

The iOS and Android React Native source is in this `mobile/` directory, not `native/` (which holds the web dashboard). GitHub Actions verifies the JavaScript export but **does not** create an Apple-signed .ipa. EAS project `@bferrell514/therounders` (`40f4305a-ef4e-48bf-aedf-f16068e20791`) is already linked. A signed build still has to be requested explicitly.

1. Stay on Expo account `bferrell514`. Do not run `eas init` again unless `expo.extra.eas.projectId` is removed. Confirm the bundle identifier `com.bthecoderr.therounders` belongs to the intended Apple Developer account before generating certificates. It is not yet registered with Expo Apple credentials, and no public App Store record exists for it.
2. The production Rounders API origin is `https://therounders.netlify.app`. It is set on the production EAS build profile as `EXPO_PUBLIC_ROUNDERS_API_URL`. Only this public origin can go in a client-side `EXPO_PUBLIC_` variable; keep sportsbook provider keys on the backend. The production EAS profile is explicitly mapped to the production environment. The deployed feed is still the controlled demo provider until a live odds key is configured on the server, and the app must keep that state labeled simulated.
3. Configure iOS distribution credentials and App Store Connect API access in your own Expo/Apple accounts (`npx eas-cli credentials --platform ios`). Check that the correct app exists in App Store Connect and supply its numeric `ascAppId` in `eas.json > submit.production.ios` before attempting a noninteractive upload.
4. Use the approved sports-R primary artwork as the iOS/Android icon. Save its 1024x1024 RGB PNG as `mobile/assets/icon.png`, then set `expo.icon` to `./assets/icon.png` in `mobile/app.json`. Keep the analytics-R design as alternate marketing artwork. Take real-device screenshots and confirm the market-feed mode is accurately labeled.
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

The full-resolution approved 1024x1024 primary and alternate sports artwork must be added to the repo as binary files from the brand-asset package. Those PNG binaries are not part of this workflow-only PR, and setting an icon path without uploading the file will fail preflight/Expo export.
