import test from "node:test";
import assert from "node:assert/strict";
import {auditCoverage} from "../lib/research/coverage.ts";
import {fitWeights,weightedMargin} from "../lib/research/weightedEnsemble.ts";
test("coverage flags unknown teams and rejects late locks",()=>{
 const startsAt="2026-11-25T00:00:00Z";
 const result=auditCoverage([{eventId:"1",startsAt,home:"A",away:"B"}],[{provider_event_id:"1",model_id:"v2",predicted_at:startsAt,starts_at:startsAt}],["v2"],new Set(["A"]),new Date("2026-11-24T00:00:00Z"));
 assert.equal(result[0].reason,"missing-team-history");assert.deepEqual(result[0].missingModels,["v2"]);
});
test("weights exclude future settlements and favor lower error",()=>{
 const row={eventId:"1",startsAt:"2025-01-01",settledAt:"2025-01-02",actualMargin:10,margins:{a:9,b:0}};
 const fit=fitWeights([row,{...row,eventId:"2",settledAt:"2027-01-01",margins:{a:-100,b:10}}],["a","b"],new Date("2026-01-01"),1);
 assert.equal(fit.games,1);assert.ok(fit.weights.a>fit.weights.b);assert.equal(weightedMargin({a:9},fit.weights),null);
});
test("small sample falls back to equal weights",()=>{assert.deepEqual(fitWeights([],["a","b"],new Date()).weights,{a:0.5,b:0.5});});
