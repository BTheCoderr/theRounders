import test from "node:test";
import assert from "node:assert/strict";
import {parseArchiveMonth,fetchRegularArchiveMonth} from "../lib/results/espnArchive.ts";

function event(id,phase=2,date="2025-02-10T19:00:00Z"){
 return {id,date,season:{year:2025,type:phase,slug:"regular-season"},
  status:{type:{completed:true}},competitions:[{
   neutralSite:false,competitors:[
    {homeAway:"home",score:"118",team:{id:"2",displayName:"Boston Celtics"}},
    {homeAway:"away",score:"99",team:{id:"18",displayName:"New York Knicks"}}
   ]
  }]};
}

test("deduplicate genuine regular-season finals by event id and record stable team ids",()=>{
 const result=parseArchiveMonth([event("A"),event("A")],"202502");
 assert.equal(result.games.length,1);
 assert.equal(result.games[0].homeId,"2");
 assert.equal(result.games[0].awayId,"18");
 assert.equal(result.games[0].eventId,"A");
 assert.equal(result.games[0].season,2025);
 assert.equal(result.unknown,0);
});
test("exclude exhibition/preseason and playoff results, and ignore games from other months",()=>{
 const result=parseArchiveMonth([
  event("PS",1),event("POST",3),event("OFF",4),
  event("WRONG",2,"2025-03-10T00:00:00Z"),
  event("REG",2)
 ],"202502");
 assert.deepEqual(result.games.map(x=>x.eventId),["REG"]);
 assert.equal(result.excluded,3);
 assert.equal(result.completedSeen,4);
});
test("fail to classify absent phase, provider id or team identifiers",()=>{
 const bad=[event("NO_PHASE"),event("NO_TEAM"),event("NO_EVENT")];
 delete bad[0].season;
 delete bad[1].competitions[0].competitors[0].team.id;
 delete bad[2].id;
 const result=parseArchiveMonth(bad,"202502");
 assert.equal(result.games.length,0);
 assert.equal(result.unknown,3);
});
test("ignore incomplete and future-phase events as training history",()=>{
 const pending=event("P");pending.status.type.completed=false;
 const result=parseArchiveMonth([pending,event("PS",1)],"202502");
 assert.equal(result.games.length,0);
 assert.equal(result.excluded,1);
});
test("reject malformed completed event batches rather than mark a missing archive month complete",async()=>{
 const original=globalThis.fetch;
 try{
  globalThis.fetch=async()=>({ok:true,json:async()=>({events:[event("BAD",2)]})});
  const valid=await fetchRegularArchiveMonth("NBA","202502");
  assert.equal(valid.games.length,1);
  globalThis.fetch=async()=>({ok:true,json:async()=>({events:[event("UNKNOWN",2),{...event("missing"),season:undefined}]})});
  await assert.rejects(()=>fetchRegularArchiveMonth("NBA","202502"),/without trustworthy phase or identity/);
 }finally{globalThis.fetch=original}
});
test("reject invalid historical queries and truncated provider pages",async()=>{
 await assert.rejects(()=>fetchRegularArchiveMonth("NCAAF","202502"),/Invalid sport or month/);
 await assert.rejects(()=>fetchRegularArchiveMonth("NBA","202513"),/Invalid sport or month/);
 const original=globalThis.fetch;
 try{
  globalThis.fetch=async()=>({ok:true,json:async()=>({events:new Array(1000).fill({})})});
  await assert.rejects(()=>fetchRegularArchiveMonth("NBA","202502"),/missing\/truncated/);
 }finally{globalThis.fetch=original}
});
