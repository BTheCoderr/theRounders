import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

const root=new URL("../../",import.meta.url);
const toml=readFileSync(new URL("netlify.toml",root),"utf8");
const sports=["nba","nfl","nhl","mlb"];
const ticks=[0,15,30,45];
test("every league has an explicit three-hour history schedule",()=>{
 sports.forEach((sport,i)=>{
  const section=`[functions."rounders-history-${sport}"]`;
  assert.ok(toml.includes(section));
  assert.ok(toml.slice(toml.indexOf(section),toml.indexOf(section)+85)
    .includes(`schedule = "${ticks[i]} */3 * * *"`));
  const fn=readFileSync(new URL(`native/netlify/functions/rounders-history-${sport}.ts`,root),"utf8");
  assert.match(fn,/runScheduledSport/);
  assert.ok(fn.includes(`schedule:"${ticks[i]} */3 * * *"`));
 });
});
test("daily model evaluation is isolated from ingestion",()=>{
 sports.forEach((sport,i)=>{
  const section=`[functions."rounders-evaluation-${sport}"]`;
  assert.ok(toml.includes(section));
  assert.ok(toml.slice(toml.indexOf(section),toml.indexOf(section)+85)
    .includes(`schedule = "${ticks[i]} 14 * * *"`));
  const fn=readFileSync(new URL(`native/netlify/functions/rounders-evaluation-${sport}.ts`,root),"utf8");
  assert.match(fn,/runScheduledEvaluation/);
  assert.ok(fn.includes(`schedule:"${ticks[i]} 14 * * *"`));
 });
 const runner=readFileSync(new URL("native/lib/persistence/scheduleRun.ts",root),"utf8");
 const importer=runner.slice(runner.indexOf("export async function runScheduledSport"),runner.indexOf("export async function runScheduledEvaluation"));
 assert.doesNotMatch(importer,/recordModelEvaluation\(|saveComparison\(/);
});
