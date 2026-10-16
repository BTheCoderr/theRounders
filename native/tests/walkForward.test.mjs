import test from "node:test";
import assert from "node:assert/strict";
import {compareWalkForward,fitMasseyRidge,fitElo} from "../lib/walkForward.ts";

const start=Date.UTC(2024,0,1);
function history(weeks=80,includeFuture=false){
 const teams=["BOS","NYK","LAL","GSW"],rows=[];
 for(let w=0;w<weeks;w++){
  const date=new Date(start+w*7*86400000).toISOString();
  const home=teams[w%4],away=teams[(w+1)%4];
  const strengths={BOS:9,NYK:4,LAL:-3,GSW:-10};
  const margin=strengths[home]-strengths[away]+2+(w%3-1);
  rows.push({date,team:home,opponent:away,teamScore:100+Math.max(0,margin),opponentScore:100+Math.max(0,-margin),location:"home"});
  rows.push({date,team:away,opponent:home,teamScore:100+Math.max(0,-margin),opponentScore:100+Math.max(0,margin),location:"away"});
 }
 if(includeFuture)rows.push({date:"2030-01-01T00:00:00Z",team:"NYK",opponent:"BOS",teamScore:500,opponentScore:0,location:"home"});
 return rows;
}
const asOf=new Date("2025-10-01T00:00:00Z");
test("all four models use the exact same held-out games",()=>{
 const r=compareWalkForward(history(),"NBA",asOf);
 assert.ok(r.evaluatedWeeks>=4);
 assert.ok(r.evaluatedGames>=10);
 assert.deepEqual(r.models.map(x=>x.games),Array(5).fill(r.evaluatedGames));
 assert.ok(r.models.some(x=>x.model==="rounders-research-v2.1"));
 assert.ok(r.models.every(x=>x.mae!==null&&Number.isFinite(x.mae)));
 assert.match(r.warning,/diagnostic|not independently validated/i);
});
test("future outcomes cannot affect any past evaluation",()=>{
 const normal=compareWalkForward(history(),"NBA",asOf);
 const future=compareWalkForward(history(80,true),"NBA",asOf);
 assert.deepEqual(future,normal);
});
test("regularized Massey comparator remains centered and finite",()=>{
 const rows=[{date:"2024-01-01",home:"Strong",away:"Average",homeScore:120,awayScore:100,neutral:false},
  {date:"2024-01-02",home:"Average",away:"Weak",homeScore:110,awayScore:95,neutral:false}];
 const r=fitMasseyRidge(rows,2.2);
 assert.ok((r.get("Strong")??0)>(r.get("Weak")??0));
 assert.ok(Math.abs([...r.values()].reduce((a,b)=>a+b,0))<0.001);
});
test("Elo updates from completed matches only",()=>{
 const game={date:"2024-01-01",home:"A",away:"B",homeScore:110,awayScore:90,neutral:false};
 assert.equal(fitElo([],0.04,2.2).size,0);
 const r=fitElo([game],0.04,2.2);
 assert.ok((r.get("A")??0)>1500);
 assert.ok((r.get("B")??0)<1500);
});
test("cold starts do not claim to beat a comparator",()=>{
 const r=compareWalkForward(history(3),"NBA",asOf);
 assert.equal(r.evaluatedGames,0);
 assert.equal(r.bestByMAE,null);
 assert.equal(r.betterThanBaseline,null);
 assert.match(r.warning,/insufficient/i);
});
test("later games cannot change a prior as-of report",()=>{
 const rows=history(21),updated=rows.map(x=>({...x}));
 for(const g of updated.slice(-2))g.teamScore+=40;
 const end=new Date(Date.parse(rows[rows.length-1].date)-86400000);
 assert.deepEqual(compareWalkForward(rows,"NBA",end),compareWalkForward(updated,"NBA",end));
});
test("cap the benchmark window to prevent runaway work",()=>{
 assert.throws(()=>compareWalkForward(history(),"NBA",asOf,10000),/Invalid evaluation window/);
});
