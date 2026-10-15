import test from "node:test";
import assert from "node:assert/strict";
import {getEspnMonthResults} from "../lib/results/espn.ts";

const original=globalThis.fetch;
test("month filter excludes other dates and incomplete games",async()=>{
 const events=[
  {date:"2025-06-04T02:00:00Z",status:{type:{completed:true}},
   competitions:[{competitors:[{homeAway:"home",score:"110",team:{displayName:"Boston Celtics"}},{homeAway:"away",score:"100",team:{displayName:"New York Knicks"}}]}]},
  {date:"2025-07-01T02:00:00Z",status:{type:{completed:true}},
   competitions:[{competitors:[{homeAway:"home",score:"3",team:{displayName:"Boston Celtics"}},{homeAway:"away",score:"2",team:{displayName:"New York Knicks"}}]}]},
  {date:"2025-06-20T02:00:00Z",status:{type:{completed:false}},
   competitions:[{competitors:[{homeAway:"home",score:"0",team:{displayName:"Boston Celtics"}},{homeAway:"away",score:"0",team:{displayName:"New York Knicks"}}]}]}
 ];
 try{
  globalThis.fetch=async url=>{
   assert.match(String(url),/dates=202506&limit=1000/);
   return {ok:true,json:async()=>({events})};
  };
  const result=await getEspnMonthResults("NBA","202506");
  assert.equal(result.length,2);
  assert.deepEqual(result.map(x=>x.team),["Boston Celtics","New York Knicks"]);
 }finally{globalThis.fetch=original}
});
test("empty off-season months are valid rather than provider failures",async()=>{
 try{
  globalThis.fetch=async()=>({ok:true,json:async()=>({events:[]})});
  assert.deepEqual(await getEspnMonthResults("NBA","202507"),[]);
 }finally{globalThis.fetch=original}
});
test("oversized month feeds fail closed instead of silently truncating rankings",async()=>{
 try{
  globalThis.fetch=async()=>({ok:true,json:async()=>({events:Array(1000).fill({})})});
  await assert.rejects(()=>getEspnMonthResults("NBA","202501"),/truncated/);
 }finally{globalThis.fetch=original}
});
test("reject invalid month values before calling public scoreboard",async()=>{
 await assert.rejects(()=>getEspnMonthResults("NBA","202513"),/Invalid month/);
 await assert.rejects(()=>getEspnMonthResults("NBA","2025-01"),/Invalid month/);
});
