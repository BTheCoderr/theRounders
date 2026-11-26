import test from "node:test";
import assert from "node:assert/strict";
import {parseEspnLines,lineNumber,moneyline} from "../lib/results/espnLines.ts";
import {computePowerBoard} from "../lib/powerRatings.ts";
import {fitPowerV3} from "../lib/engine/powerV3.ts";
import {runBacktest} from "../lib/engine/backtest.ts";

const ev=(odds,state="pre")=>({id:"401",date:"2026-12-01T00:30:00Z",status:{type:{state}},competitions:[{
 competitors:[{homeAway:"home",team:{id:"2",displayName:"Boston Celtics",abbreviation:"BOS"}},{homeAway:"away",team:{id:"18",displayName:"New York Knicks",abbreviation:"NY"}}],
 odds:odds?[odds]:undefined}]});
test("ESPN lines: home spread sign must be confirmed, never guessed",()=>{
 assert.equal(lineNumber("o220.5"),220.5);assert.equal(lineNumber("PK"),0);assert.equal(lineNumber("abc"),null);
 assert.equal(moneyline("EVEN"),100);assert.equal(moneyline("-50"),null);
 // favorite flag + details agree: home -5.5
 let [l]=parseEspnLines([ev({provider:{name:"DraftKings"},details:"BOS -5.5",spread:-5.5,overUnder:221.5,homeTeamOdds:{favorite:true,moneyLine:-220},awayTeamOdds:{favorite:false,moneyLine:180}})],"NBA");
 assert.equal(l.spreadHome,-5.5);assert.equal(l.total,221.5);assert.equal(l.book,"DraftKings");
 assert.ok(l.homeWinProb>0.65&&l.homeWinProb<0.7);
 // away favorite from details only: home +3
 [l]=parseEspnLines([ev({details:"NY -3",overUnder:215})],"NBA");assert.equal(l.spreadHome,3);
 // contradictory signals: spread null, total still kept
 [l]=parseEspnLines([ev({details:"NY -3",overUnder:215,homeTeamOdds:{favorite:true}})],"NBA");assert.equal(l.spreadHome,null);assert.equal(l.total,215);
 // no sign source at all: null
 [l]=parseEspnLines([ev({spread:4,overUnder:215})],"NBA");assert.equal(l.spreadHome,null);
 // open/close pairs
 [l]=parseEspnLines([ev({pointSpread:{home:{open:{line:"-4"},close:{line:"-6.5"}},away:{open:{line:"+4"},close:{line:"+6.5"}}},total:{over:{open:{line:"o219"},close:{line:"o222"}}}})],"NBA");
 assert.equal(l.spreadHome,-6.5);assert.equal(l.open.spreadHome,-4);assert.equal(l.total,222);assert.equal(l.open.total,219);
 // implausible values and started games are dropped
 assert.equal(parseEspnLines([ev({details:"BOS -80",overUnder:999})],"NBA").length,0);
 assert.equal(parseEspnLines([ev({details:"BOS -5",overUnder:220},"in")],"NBA").length,0);
 assert.equal(parseEspnLines([ev(null)],"NBA").length,0);
});

const league=()=>{const teams="ABCDEFGHIJ".split(""),str=Object.fromEntries(teams.map((t,i)=>[t,(5-i)*2]));
 let seed=3;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;const rows=[];
 for(const y of [2023,2024,2025])for(let d=0;d<(y===2025?20:150);d++)for(let k=0;k<4;k++){
  const h=teams[Math.floor(rnd()*10)];let a=teams[Math.floor(rnd()*10)];if(a===h)a=teams[(teams.indexOf(h)+1)%10];
  const m=Math.round(str[h]-str[a]+3+(rnd()-0.5)*24);
  rows.push({date:new Date(Date.UTC(y,9,20)+d*864e5+k*36e5).toISOString(),team:h,opponent:a,teamScore:110+Math.max(m,0),opponentScore:110+Math.max(-m,0)+(m===0?1:0),location:"home"});}
 return rows;};
test("power board without a prior is unchanged; a prior pulls toward it",()=>{
 const rows=league().slice(0,40),asOf=new Date("2024-01-01");
 const a=computePowerBoard(rows,"NBA",asOf),b=computePowerBoard(rows,"NBA",asOf,undefined);
 assert.deepEqual(a.rankings,b.rankings);
 const target=new Map(a.rankings.map(r=>[r.team,r.team==="J"?20:r.rating]));
 const c=computePowerBoard(rows,"NBA",asOf,{ratings:target,weight:50});
 assert.ok(c.rankings.find(r=>r.team==="J").rating>a.rankings.find(r=>r.team==="J").rating+3);
});
test("power-v3: prior fades during the season and rest is estimated from training only",()=>{
 const rows=league();const games=rows.map(r=>({date:r.date,home:r.team,away:r.opponent,homeScore:r.teamScore,awayScore:r.opponentScore,neutral:false}));
 const early=fitPowerV3(games,"NBA",new Date("2025-10-25T00:00:00Z")),late=fitPowerV3(games,"NBA",new Date("2026-03-01T00:00:00Z"));
 assert.ok(early.priorWeight>late.priorWeight&&early.priorWeight<=8);
 assert.ok(Number.isFinite(early.restPointsPerDay));
 assert.equal(early.predict("A","Z",false),null);
 assert.ok(early.predict("A","J",false)>0);
});
test("backtest stops cleanly at the time budget",()=>{
 const r=runBacktest(league(),"NBA",new Date("2025-11-15T00:00:00Z"),{maxWeeks:30,minTrainGames:60,budgetMs:1,models:["power-v2","power-v3"]});
 assert.equal(r.truncated,true);
 const full=runBacktest(league(),"NBA",new Date("2025-11-15T00:00:00Z"),{maxWeeks:30,minTrainGames:60,models:["power-v2","power-v3"]});
 assert.ok(!full.truncated&&full.models.find(m=>m.model==="power-v3").summary.games===full.evaluatedGames);
});
