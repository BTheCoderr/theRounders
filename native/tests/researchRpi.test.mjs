import test from "node:test";
import assert from "node:assert/strict";
import {fitResearchRpi} from "../lib/researchRpi.ts";
import {auditGameHistory,seasonYear} from "../lib/researchDataQuality.ts";

const at=new Date("2026-10-16T00:00:00Z");
function game(date,home,away,h,a,neutral=false){
 return [
  {date,team:home,opponent:away,teamScore:h,opponentScore:a,location:neutral?"neutral":"home"},
  {date,team:away,opponent:home,teamScore:a,opponentScore:h,location:neutral?"neutral":"away"}
 ];
}
test("new model fits only completed results strictly before cutoff, and deduplicates mirrored rows",()=>{
 const rows=[...game("2026-10-10","A","B",120,100),
  ...game("2026-10-16T00:00:00Z","B","A",999,0),
  ...game("2026-10-20","A","B",900,1)];
 const base=fitResearchRpi(rows.slice(0,2),"NBA",at);
 const extended=fitResearchRpi(rows,"NBA",at);
 assert.equal(base.games,1);assert.equal(extended.games,1);
 assert.deepEqual([...base.ratings],[...extended.ratings]);
 assert.equal(base.homeAdvantage,extended.homeAdvantage);
 assert.equal(base.model,"rounders-research-v2.1");
});
test("neutral-site games never contribute to fitted home advantage",()=>{
 const rows=[];
 for(let i=0;i<24;i++)rows.push(...game(new Date(Date.parse("2026-09-01")+i*86400000).toISOString(),i%2?"B":"A",i%2?"A":"B",110,100,true));
 const result=fitResearchRpi(rows,"NBA",at);
 assert.equal(result.homeAdvantage,2.2);
});
test("two-sided home results move the league home estimate without masquerading as team quality",()=>{
 const rows=[];
 for(let i=0;i<40;i++)rows.push(...game(new Date(Date.parse("2026-08-01")+i*86400000).toISOString(),i%2?"B":"A",i%2?"A":"B",110,102));
 const result=fitResearchRpi(rows,"NBA",at);
 assert.ok(result.homeAdvantage>2.2);
 assert.ok(Math.abs((result.ratings.get("A")||0)-(result.ratings.get("B")||0))<1.0);
});
test("robust residual weighting reduces sensitivity to one extreme blowout",()=>{
 const rows=[];
 for(let i=0;i<25;i++)rows.push(...game(new Date(Date.parse("2026-09-01")+i*86400000).toISOString(),"A","B",101,100));
 rows.push(...game("2026-09-30","A","B",400,100));
 const huber=fitResearchRpi(rows,"NBA",at,{huberDelta:6});
 const square=fitResearchRpi(rows,"NBA",at,{huberDelta:100000});
 const gap=(x)=>Math.abs((x.ratings.get("A")||0)-(x.ratings.get("B")||0));
 assert.ok(gap(huber)<gap(square));
});
test("sparse disconnected schedules give finite centered ratings",()=>{
 const result=fitResearchRpi([...game("2026-10-01","A","B",3,1),...game("2026-10-02","C","D",10,9)],"NHL",at);
 assert.equal(result.ratings.size,4);
 assert.ok([...result.ratings.values()].every(Number.isFinite));
 assert.ok(Math.abs([...result.ratings.values()].reduce((a,b)=>a+b,0))<0.001);
});
test("invalid solver settings fail explicitly",()=>{
 assert.throws(()=>fitResearchRpi([],"NBA",at,{ridge:0}),/Invalid research/);
 assert.throws(()=>fitResearchRpi([],"NBA",at,{priorRetention:1.1}),/Invalid research/);
});
test("season boundaries are sport aware and do not mistake December for a different league season",()=>{
 assert.equal(seasonYear("NBA","2025-02-01"),2024);
 assert.equal(seasonYear("NFL","2025-01-31"),2024);
 assert.equal(seasonYear("MLB","2025-04-01"),2025);
});
test("a few games never qualify as validated multi-season history",()=>{
 const audit=auditGameHistory([...game("2024-10-01","A","B",112,101),...game("2026-10-01","C","D",100,93)],"NBA");
 assert.equal(audit.researchReady,false);
 assert.equal(audit.seasons.length,2);
 assert.match(audit.warnings.join(" "),/Fewer than five/i);
});
test("simulated input can never pass research readiness",()=>{
 const audit=auditGameHistory(game("2026-10-01","A","B",99,98),"NBA","controlled-demo","simulated");
 assert.equal(audit.researchReady,false);
 assert.match(audit.warnings.join(" "),/SIMULATED/);
});
