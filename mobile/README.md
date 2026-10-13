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
