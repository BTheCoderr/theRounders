import test from "node:test";
import assert from "node:assert/strict";
import {edgePick,edgeRecord} from "../lib/engine/edge.ts";
import {parseArchiveMonth,teamStats} from "../lib/results/espnArchive.ts";

const base={eventId:"1",startsAt:"2026-11-27T00:00:00Z",home:"H",away:"A",homeWinProbability:0.6,marketHomeProb:null,lineSource:"x",lineAt:null,finalHome:null,finalAway:null};
test("spread edges need the threshold and grade against the line",()=>{
 assert.equal(edgePick({...base,sport:"NBA",projectedMargin:5,marketSpreadHome:-3}),null);           // 2-point edge < 3
 const p=edgePick({...base,sport:"NBA",projectedMargin:8,marketSpreadHome:-3,finalHome:110,finalAway:104});
 assert.equal(p.side,"H");assert.equal(p.edge,5);assert.equal(p.result,"win");                      // won by 6, covered -3
 const q=edgePick({...base,sport:"NBA",projectedMargin:-2,marketSpreadHome:-3,finalHome:110,finalAway:108});
 assert.equal(q.side,"A");assert.equal(q.result,"win");                                              // home won by 2, didn't cover -3
 assert.equal(edgePick({...base,sport:"NBA",projectedMargin:8,marketSpreadHome:-3,finalHome:103,finalAway:100}).result,"push");
 assert.equal(edgePick({...base,sport:"NBA",projectedMargin:8,marketSpreadHome:null}),null);
});
test("NHL/MLB edges use market probability; record reports break-even honestly",()=>{
 const a=edgePick({...base,sport:"NHL",projectedMargin:0.5,homeWinProbability:0.62,marketSpreadHome:-1.5,marketHomeProb:0.5,finalHome:2,finalAway:3});
 assert.equal(a.kind,"moneyline");assert.equal(a.side,"H");assert.equal(a.result,"loss");assert.equal(a.marketProbForSide,0.5);
 assert.equal(edgePick({...base,sport:"NHL",projectedMargin:0.1,homeWinProbability:0.53,marketSpreadHome:-1.5,marketHomeProb:0.5}),null);
 const r=edgeRecord([a,{...a,result:"win",marketProbForSide:0.4}]);
 assert.equal(r.wins,1);assert.equal(r.losses,1);assert.equal(r.breakEven,0.45);
 const s=edgeRecord([edgePick({...base,sport:"NBA",projectedMargin:8,marketSpreadHome:-3,finalHome:110,finalAway:104})]);
 assert.equal(s.breakEven,0.524);assert.equal(edgeRecord([]).breakEven,null);
});
test("archive keeps numeric team box totals when ESPN provides them",()=>{
 assert.deepEqual(teamStats({statistics:[{name:"fieldGoalsAttempted",displayValue:"58"},{name:"fieldGoalPct",displayValue:"45.2"},{name:"avgPoints",displayValue:"-"},{name:"rec",displayValue:"5-2"}]}),{fieldGoalsAttempted:58,fieldGoalPct:45.2});
 assert.equal(teamStats({}),null);
 const e={id:"9",date:"2026-11-20T00:00:00Z",season:{type:2,year:2027},status:{type:{completed:true}},competitions:[{competitors:[
  {homeAway:"home",score:"70",team:{id:"1",displayName:"H"},statistics:[{name:"fieldGoalsAttempted",displayValue:"60"}]},
  {homeAway:"away",score:"65",team:{id:"2",displayName:"A"},statistics:[{name:"fieldGoalsAttempted",displayValue:"55"}]}]}]};
 const m=parseArchiveMonth([e],"202611");
 assert.deepEqual(m.games[0].box,{home:{fieldGoalsAttempted:60},away:{fieldGoalsAttempted:55}});
 const n=parseArchiveMonth([{...e,competitions:[{competitors:e.competitions[0].competitors.map(c=>({...c,statistics:undefined}))}]}],"202611");
 assert.equal(n.games[0].box,null);
});
