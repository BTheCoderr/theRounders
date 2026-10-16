#!/usr/bin/env bash
# Install the exact approved sports-R PNG, then push ONLY the app configuration and icon.
# Usage: bash mobile/scripts/install-approved-icon.sh /absolute/path/to/therounders-primary-icon.png
set -euo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[ "$#" -eq 1 ] || fail "Usage: bash mobile/scripts/install-approved-icon.sh /path/to/therounders-primary-icon.png"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC="$1"
DST="$REPO/mobile/assets/icon.png"
APP="$REPO/mobile/app.json"
EXPECTED_SHA="377fa28d0df652926debe87146a186682ed99df8aecb4741dc8102c8ed3449d4"

command -v git >/dev/null || fail "git required"
command -v node >/dev/null || fail "Node.js required"
command -v shasum >/dev/null || fail "shasum required (macOS)"
[ -f "$SRC" ] || fail "Approved PNG file not found: $SRC"
[ -f "$APP" ] || fail "Missing mobile/app.json"
[ -f "$REPO/mobile/eas.json" ] || fail "Missing mobile/eas.json"
[ -f "$REPO/mobile/scripts/release-preflight.mjs" ] || fail "Missing release preflight"
[ "$(git -C "$REPO" branch --show-current)" = "main" ] || fail "Switch to main branch first"
[ -z "$(git -C "$REPO" status --porcelain)" ] || fail "Working tree is not clean"
ORIGIN="$(git -C "$REPO" remote get-url origin)"
[[ "$ORIGIN" == *"BTheCoderr/theRounders"* ]] || fail "Unexpected GitHub remote. Check origin."
[ "$(shasum -a 256 "$SRC" | awk '{print $1}')" = "$EXPECTED_SHA" ] || fail "Wrong artwork or changed file. Refusing to install."

# Never reinitialize the linked Expo project.
node - "$APP" <<'NODE'
const fs = require("node:fs");
const app = JSON.parse(fs.readFileSync(process.argv[2], "utf8")).expo;
if (app?.owner !== "bferrell514" ||
    app?.slug !== "therounders" ||
    app?.ios?.bundleIdentifier !== "com.bthecoderr.therounders" ||
    app?.extra?.eas?.projectId !== "40f4305a-ef4e-48bf-aedf-f16068e20791") {
  console.error("Unexpected Rounders Expo project: aborting.");
  process.exit(1);
}
if (app.icon && app.icon !== "./assets/icon.png") {
  console.error("Different app icon already configured: aborting.");
  process.exit(1);
}
NODE

git -C "$REPO" fetch --quiet origin main
[ "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse refs/remotes/origin/main)" ] || fail "Local main is behind/ahead of remote. Run git pull --ff-only, then retry."

[ ! -e "$DST" ] || fail "An icon already exists; refusing to overwrite"
mkdir -p "$(dirname "$DST")"
cp "$SRC" "$DST"
node - "$APP" <<'NODE'
const fs = require("node:fs");
const path = process.argv[2];
const data = JSON.parse(fs.readFileSync(path, "utf8"));
data.expo.icon = "./assets/icon.png";
fs.writeFileSync(path, JSON.stringify(data, null, 2) + "\n");
NODE

if ! (cd "$REPO/mobile" && node scripts/release-preflight.mjs); then
  printf '%s\n' "Preflight failed. Changes are local and not committed. Inspect before retrying." >&2
  exit 1
fi

git -C "$REPO" add -- mobile/app.json mobile/assets/icon.png
git -C "$REPO" diff --cached --quiet && fail "No icon changes to commit"
git -C "$REPO" commit -m "Add verified approved sports-R app icon"
git -C "$REPO" push origin main
printf '\nApproved icon and Expo config pushed. No paid EAS build or submission was started.\n'
