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

The iOS and Android React Native source is in this `mobile/` directory, not `native/` (which holds the web dashboard). GitHub Actions verifies the JavaScript export but **does not** create an Apple-signed .ipa until EAS is linked and a build is requested.

1. From `mobile/`, sign in with your own Expo account using `npx eas-cli login`, then run `npx eas-cli init`. Commit the generated `expo.extra.eas.projectId` to `mobile/app.json`. Confirm the bundle identifier `com.bthecoderr.therounders` belongs to your intended Apple Developer account before generating certificates.
2. In Expo's project settings, set `EXPO_PUBLIC_ROUNDERS_API_URL` to your deployed HTTPS Rounders API **in the production environment**. Only this public origin can go in a client-side `EXPO_PUBLIC_` variable; keep sportsbook provider keys on the backend. The production EAS profile is explicitly mapped to the production environment.
3. Configure iOS distribution credentials and App Store Connect API access in your own Expo/Apple accounts (`npx eas-cli credentials --platform ios`). Check that the correct app exists in App Store Connect and supply its numeric `ascAppId` in `eas.json > submit.production.ios` before attempting a noninteractive upload.
4. Replace Expo's generic icon with a reviewed 1024x1024 nontransparent app icon and add the asset path to `app.json`. Take real-device/screenshots and confirm the market-feed mode is accurately labeled.
5. On GitHub, add `EXPO_TOKEN` under repository **Settings → Secrets and variables → Actions**. Do not commit credentials or the token.
6. Run **Actions → therounders iOS TestFlight (manual) → Run workflow**. Leave `submit_to_testflight` unchecked to create only an Apple-signed store build. Choose it only when TestFlight submission is explicitly desired and the App Store Connect API key is configured.

Alternatively, once setup is complete, run locally from `mobile/`:
```sh
npx eas-cli build --platform ios --profile production
npx eas-cli submit --platform ios --profile production
```

A passing Expo JavaScript export is **not** evidence that an .ipa was signed, a tester installed it, or Apple accepted it. No real wagering is included.
