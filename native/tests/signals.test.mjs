import test from "node:test";
import assert from "node:assert/strict";
import {findLineShopGaps} from "../lib/signals.ts";

function quote(overrides={}) {
 return {eventId:"nba-a",sport:"NBA",market:"spread",selection:"BOS",line:-3.5,
  price:-110,book:"Book A",updatedAt:"2026-10-13T18:00:00Z",state:"live",
  away:"NYK",home:"BOS",startTime:"2026-10-13T21:00:00Z",...overrides};
}
test("compares prices only for the same event, market, selection and line",()=>{
 const gaps=findLineShopGaps([
  quote({book:"A",price:-110}),
  quote({book:"B",price:105}),
  quote({book:"C",price:200,line:-4.5}),
  quote({book:"D",price:300,market:"moneyline"})
 ]);
 assert.equal(gaps.length,1);
 assert.equal(gaps[0].bestBook,"B");
 assert.equal(gaps[0].worstBook,"A");
 assert.equal(gaps[0].line,-3.5);
});
test("never manufactures a steam alert from one sportsbook",()=>{
 assert.deepEqual(findLineShopGaps([quote()]),[]);
});
test("does not combine real and simulated price feeds",()=>{
 assert.deepEqual(findLineShopGaps([quote({book:"A"}),quote({book:"B",price:110,state:"simulated"})]),[]);
});
test("rejects malformed prices and deduplicates same sportsbook",()=>{
 const rows=findLineShopGaps([quote({book:"A",price:0}),quote({book:"A",price:-120}),quote({book:"A",price:-110}),quote({book:"B",price:130})]);
 assert.equal(rows.length,1);
 assert.equal(rows[0].bestBook,"B");
 assert.equal(rows[0].worstPrice,-110);
});
test("outputs implied percentage-point price difference, not confidence",()=>{
 const [gap]=findLineShopGaps([quote({book:"A",price:-110}),quote({book:"B",price:110})]);
 assert.ok(gap.impliedGapPoints>4&&gap.impliedGapPoints<6);
 assert.equal(gap.state,"live");
});
