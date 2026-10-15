import test from "node:test";
import assert from "node:assert/strict";
import {computePowerBoard,uniqueCompletedGames,holdoutMarginEvaluation} from "../lib/powerRatings.ts";

const now=new Date("2026-10-15T15:00:00Z");
const game=(date,home,away,hs,as)=>[
 {date,team:home,opponent:away,teamScore:hs,opponentScore:as,location:"home"},
 {date,team:away,opponent:home,teamScore:as,opponentScore:hs,location:"away"}
];

test("mirrored input counts each played match only once",()=>{
 const rows=[...game("2026-10-10","Boston Celtics","New York Knicks",112,103)];
 const normalized=uniqueCompletedGames(rows,now);
 assert.equal(normalized.length,1);
 const board=computePowerBoard(rows,"NBA",now);
 assert.equal(board.games,1);
 assert.equal(board.rankings.length,2);
 assert.equal(board.rankings.find(r=>r.team==="Boston Celtics").games,1);
});

test("future, invalid scores and duplicate rows cannot affect rankings",()=>{
 const rows=[...game("2026-10-10","A","B",110,100),
 ...game("2026-10-17","B","A",999,0),
 {date:"2026-10-09",team:"A",opponent:"B",teamScore:NaN,opponentScore:0,location:"home"},
 ...game("2026-10-10","A","B",110,100)];
 const result=computePowerBoard(rows,"NBA",now);
 assert.equal(result.games,1);
 assert.ok(result.rankings.find(x=>x.team==="A").rating>0);
});

test("strength-of-schedule adjusts ratings across connected teams",()=>{
 const rows=[
 ...game("2026-10-10","Strong","Middle",130,100),
 ...game("2026-10-11","Middle","Weak",110,95),
 ...game("2026-10-12","Strong","Weak",120,100)
 ];
 const r=computePowerBoard(rows,"NBA",now).rankings;
 assert.deepEqual(r.map(x=>x.team),["Strong","Middle","Weak"]);
 assert.ok(r.every(x=>Number.isFinite(x.rating)&&Number.isFinite(x.averageOpponentRating)));
 assert.ok(Math.abs(r.reduce((a,b)=>a+b.rating,0))<0.05,"center at league average");
});

test("sparse disconnected opponents yield finite regularized estimates",()=>{
 const rows=[...game("2026-10-10","A","B",110,100),...game("2026-10-11","C","D",89,88)];
 const result=computePowerBoard(rows,"NBA",now);
 assert.equal(result.rankings.length,4);
 assert.ok(result.rankings.every(r=>Number.isFinite(r.rating)));
});

test("results from more recent fixtures have higher weight",()=>{
 const rows=[
 ...game("2026-07-01","A","B",120,90),
 ...game("2026-10-14","B","A",120,90)
 ];
 const ranking=computePowerBoard(rows,"NBA",now).rankings;
 assert.equal(ranking[0].team,"B");
});

test("evaluation refuses to claim improvement on insufficient history",()=>{
 const r=holdoutMarginEvaluation(game("2026-10-10","A","B",110,100),"NBA",now);
 assert.equal(r.evaluatedGames,0);
 assert.equal(r.beatsBaseline,null);
 assert.match(r.warning,/not enough/i);
});

test("evaluation uses chronological holdout and reports both baseline and model MAE",()=>{
 const teams=["A","B","C","D"];
 const rows=[];
 for(let i=0;i<36;i++){
  const home=teams[i%4],away=teams[(i+1+Math.floor(i/4)%2)%4];
  if(home===away)continue;
  const date=new Date(Date.parse("2026-08-20T12:00:00Z")+i*86400000).toISOString();
  const strength={A:12,B:5,C:-4,D:-13};
  const margin=Math.round(strength[home]-strength[away]+2);
  rows.push(...game(date,home,away,110+Math.max(0,margin),110+Math.max(0,-margin)));
 }
 const result=holdoutMarginEvaluation(rows,"NBA",now);
 assert.ok(result.evaluatedGames>=5);
 assert.ok(result.modelMAE!==null);
 assert.ok(result.homeBaselineMAE!==null);
 assert.ok(typeof result.beatsBaseline==="boolean");
 assert.equal(result.method,"chronological-70-30");
});
