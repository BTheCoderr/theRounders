# The Rounders: App Store Connect draft

Status: prepared copy only. Not submitted to Apple. Verify the release build and actual app behavior before publishing.

## Identity
- App name: theRounders
- Subtitle: Sports Ratings & Research
- Bundle ID: `com.bthecoderr.therounders`
- Expo project: `@bferrell514/therounders`
- App Store Connect `ascAppId`: **not known; enter the real numeric ID only after creating/finding the app record**
- Primary language: English (U.S.)
- Category suggestion: Sports (verify Apple review classification before selecting)
- Support URL: https://therounders.netlify.app/support
- Privacy Policy URL: https://therounders.netlify.app/privacy
- Contact: Bferrell514@gmail.com

## Promotional text (draft)
Follow sports ratings, compare market snapshots, and practice with paper-only tickets. See clearly labeled data sources and model limitations.

## App Store description (draft)
theRounders is a sports research command center for NBA, NFL, NHL, and MLB.

Explore a market board, compare prices across books at the same point line, and review experimental power ratings and model summaries. Research is transparent about whether data is live, model-based, or simulated.

Practice evaluating a matchup with on-device paper tickets. Mark outcomes and track a simulated profit and loss without placing a real-money bet.

Features:
- NBA, NFL, NHL, and MLB research boards
- Same-line price comparisons
- Experimental team power ratings and matchup model summaries
- Optional AI explanations when server-side support is available
- Paper-only ticket tracking, stored on your device
- Clear data provenance, freshness and fallback indicators

No real-money wagering, sportsbook account connections, payment processing, or guaranteed predictions are offered. Simulated fixtures and prices are not live market data. Some features require an internet connection and may be unavailable when external data providers are not configured.

## Suggested keywords
sports ratings, power rankings, basketball, football, hockey, baseball, analytics, paper tracking

## App review information
Refer to `mobile/store/app-review-notes.txt`. No account is required to use the iOS research experience. Optional website authentication is separate. Provide physical-device capture showing board, Power Index, Model Lab, Rounders AI, Price Gaps, paper tickets, Support and Privacy Policy links as implemented.

## Approval gates
- [ ] Commit the exact, checksum-verified icon (1024 × 1024, opaque)
- [ ] Confirm Apple Developer bundle ID registration
- [ ] Create/find App Store Connect record and copy its numeric Apple ID into `eas.json`
- [ ] Configure EAS iOS signing and submission permissions within your Apple/Expo accounts
- [ ] Add `EXPO_TOKEN` to GitHub Actions secrets if using the manual workflow
- [ ] Run signed production EAS build and test on a physical iPhone
- [ ] Capture real screenshots for Apple-required iPhone/iPad sizes if submitting for review
- [ ] Reconcile privacy policy with deployed telemetry, providers, data retention and App Privacy questionnaire
- [ ] Provide truthful age rating and app review answers
- [ ] Submit only when the signed build and review metadata are complete
