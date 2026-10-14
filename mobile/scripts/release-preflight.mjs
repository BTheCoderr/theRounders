#!/usr/bin/env node
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const app = JSON.parse(readFileSync(resolve(root, "app.json"), "utf8")).expo;
const eas = JSON.parse(readFileSync(resolve(root, "eas.json"), "utf8"));
const submit = process.argv.includes("--submit");
let errors = 0;
function check(ok, message) {
  console.log(`${ok ? "PASS" : "FAIL"} ${message}`);
  if (!ok) errors++;
}
function isValidIcon(icon) {
  if (typeof icon !== "string" || !icon.trim()) return false;
  const path = resolve(root, icon);
  if (!existsSync(path)) return false;
  try {
    const buffer = readFileSync(path);
    if (buffer.length < 33 || buffer.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") return false;
    const width = buffer.readUInt32BE(16);
    const height = buffer.readUInt32BE(20);
    const bitDepth = buffer[24];
    const colorType = buffer[25];
    if (width !== 1024 || height !== 1024 || bitDepth !== 8 || ![2, 3].includes(colorType)) return false;
    let offset = 8;
    while (offset + 12 <= buffer.length) {
      const length = buffer.readUInt32BE(offset);
      if (offset + length + 12 > buffer.length) return false;
      const type = buffer.toString("ascii", offset + 4, offset + 8);
      if (type === "tRNS") return false;
      if (type === "IEND") return true;
      offset += length + 12;
    }
  } catch { return false; }
  return false;
}

check(Boolean(app.extra?.eas?.projectId && /^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(app.extra.eas.projectId)), "Expo EAS project UUID linked in app.json");
check(Boolean(app.ios?.bundleIdentifier && /^([A-Za-z][A-Za-z0-9-]*\.)+[A-Za-z][A-Za-z0-9-]*$/.test(app.ios.bundleIdentifier)), "iOS bundle identifier configured");
check(isValidIcon(app.icon), "1024x1024 opaque RGB/indexed PNG configured as Expo app icon");
check(eas.build?.production?.distribution === "store", "Production EAS build uses App Store distribution");
check(eas.build?.production?.environment === "production", "Production build reads Expo production environment");
if (submit) {
  check(/^\d+$/.test(String(eas.submit?.production?.ios?.ascAppId || "")), "App Store Connect ascAppId set for automatic submission");
}
if (errors) {
  console.error(`\n${errors} iOS release preflight check(s) failed. Do not start a signed build yet.`);
  process.exit(1);
}
console.log("\nStatic iOS release checks passed. Apple signing, backend connectivity, and a physical-device test are still separate requirements.");
