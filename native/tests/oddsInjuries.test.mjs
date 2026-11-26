import test from "node:test";
import assert from "node:assert/strict";
import {spendPolicy,decideSpend,oddsCost} from "../lib/providers/spend.ts";
import {parseConsensus,matchEspn,shouldPoll,implied} from "../lib/providers/oddsApi.ts";
import {parseInjuries} from "../lib/providers/balldontlie.ts";
import {statusWeight,nbaImpacts,nflImpacts,injuryAdjustment} from "../lib/engine/injuries.ts";
import {marketReport} from "../lib/engine/clv.ts";
import {fitPlatt,plattProbability} from "../lib/engine/calibration.ts";

const on={ODDS_INGEST_ENABLED:"1",ODDS_API_KEY:"k",ODDS_MONTHLY_CREDITS:"20000"};
test("spend: off without flag, key or plan; caps month, day and provider reserve",()=>{
 assert.equal(spendPolicy("the-odds-api",{}).enabled,false);
 assert.equal(spendPolicy("the-odds-api",{ODDS_INGEST_ENABLED:"1"}).enabled,false);
 assert.equal(spendPolicy("balldontlie",{BALLDONTLIE_API_KEY:"k"}).enabled,false);
 const p=spendPolicy("the-odds-api",on);
 assert.equal(decideSpend(p,{monthUsed:0,dayUsed:0,lastRemaining:null},3).allow,true);
 assert.equal(decideSpend({...p,monthlyCredits:0},{monthUsed:0,dayUsed:0,lastRemaining:null},3).allow,false);
 assert.match(decideSpend(p,{monthUsed:16999,dayUsed:0,lastRemaining:null},3).reason,/monthly/);
 assert.match(decideSpend(p,{monthUsed:0,dayUsed:1199,lastRemaining:null},3).reason,/daily/);
 assert.match(decideSpend(p,{monthUsed:0,dayUsed:0,lastRemaining:3001},3).reason,/reserve/);
 assert.equal(oddsCost(3,1),3);
});

const ev=(books)=>({id:"e1",sport_key:"basketball_nba",commence_time:"2026-12-01T00:00:00Z",home_team:"Boston Celtics",away_team:"New York Knicks",bookmakers:books});
const book=(title,hs,tot,hp,ap)=>({key:title,title,markets:[
 {key:"spreads",outcomes:[{name:"Boston Celtics",price:-110,point:hs},{name:"New York Knicks",price:-110,point:-hs}]},
 {key:"totals",outcomes:[{name:"Over",price:-110,point:tot},{name:"Under",price:-110,point:tot}]},
 {key:"h2h",outcomes:[{name:"Boston Celtics",price:hp},{name:"New York Knicks",price:ap}]}]});
test("odds consensus: medians, vig-free probability, no imputation",()=>{
 const [c]=parseConsensus([ev([book("A",-5,220,-200,170),book("B",-6,221,-220,180),book("C",-5.5,222,-210,175)])],"NBA");
 assert.equal(c.books,3);assert.equal(c.spreadHome,-5.5);assert.equal(c.total,221);
 assert.ok(c.homeWinProb>0.6&&c.homeWinProb<0.7);
 assert.equal(c.quotes.length,18);
 assert.ok(Math.abs(implied(-110)-0.5238)<1e-3);
 assert.equal(parseConsensus([ev([])],"NBA").length,0);
 const [only]=parseConsensus([ev([{key:"x",title:"X",markets:[{key:"totals",outcomes:[{name:"Over",price:-110,point:219}]}]}])],"NBA");
 assert.equal(only.spreadHome,null);assert.equal(only.homeWinProb,null);assert.equal(only.total,219);
});
test("odds: ESPN matching and polling policy",()=>{
 const espn=[{eventId:"1",startsAt:"2026-12-01T00:30:00Z",home:"Boston Celtics",away:"New York Knicks"},
  {eventId:"2",startsAt:"2026-12-03T00:30:00Z",home:"Boston Celtics",away:"New York Knicks"}];
 assert.equal(matchEspn({home:"Boston Celtics",away:"New York Knicks",startsAt:"2026-12-01T00:00:00Z"},espn)?.eventId,"1");
 assert.equal(matchEspn({home:"New York Knicks",away:"Boston Celtics",startsAt:"2026-12-01T00:00:00Z"},espn),null);
 const now=new Date("2026-11-30T23:30:00Z");
 assert.equal(shouldPoll([],null,now).poll,false);
 assert.equal(shouldPoll(["2026-12-01T00:00:00Z"],"2026-11-30T23:10:00Z",now).reason,"closing window");
 assert.equal(shouldPoll(["2026-12-01T00:00:00Z"],"2026-11-30T23:25:00Z",now).poll,false);
 assert.equal(shouldPoll(["2026-12-02T00:00:00Z"],"2026-11-30T20:00:00Z",now).poll,false);
 assert.equal(shouldPoll(["2026-12-02T00:00:00Z"],"2026-11-30T17:00:00Z",now).reason,"opening/update");
});
test("injuries: parse, status weights, impacts and capped adjustment",()=>{
 const rows=parseInjuries([{player:{id:7,first_name:"J",last_name:"T",team:{id:2,full_name:"Boston Celtics"}},status:"Out",description:"knee"},
  {player:{id:8},status:""},{status:"Out"}]);
 assert.equal(rows.length,1);assert.equal(rows[0].team,"Boston Celtics");assert.equal(rows[0].hash.length,32);
 assert.equal(statusWeight("Questionable"),0.35);assert.equal(statusWeight("mystery"),0);assert.equal(statusWeight("Out (knee)"),1);
 const box=[];for(let g=0;g<40;g++){box.push({playerId:"7",name:"J T",team:"Boston Celtics",minutes:36,plusMinus:8});box.push({playerId:"9",name:"B",team:"Boston Celtics",minutes:10,plusMinus:-3});box.push({playerId:"9",name:"B",team:"Boston Celtics",minutes:0,plusMinus:0});}
 const imp=nbaImpacts(box);
 const star=imp.find(i=>i.playerId==="7"),bench=imp.find(i=>i.playerId==="9");
 assert.ok(star.impact>bench.impact&&star.impact<=8);assert.equal(bench.games,40);
 assert.equal(nflImpacts([{playerId:"1",name:"A",team:"X",attempts:300,games:10},{playerId:"2",name:"B",team:"X",attempts:20,games:3}]).map(q=>q.playerId).join(),"1");
 const map=new Map(imp.map(i=>[i.playerId,i]));
 const adj=injuryAdjustment("Boston Celtics","New York Knicks",[{playerId:"7",name:"J T",team:"Boston Celtics",status:"Out",reportedAt:null},{playerId:"99",name:"?",team:"Boston Celtics",status:"Out",reportedAt:null}],map);
 assert.equal(adj.players.length,1);assert.ok(adj.net<0);assert.equal(adj.home,star.impact);
 const big=new Map([["a",{playerId:"a",name:"a",team:"H",games:1,mpg:1,impact:8,method:""}],["b",{playerId:"b",name:"b",team:"H",games:1,mpg:1,impact:8,method:""}]]);
 assert.equal(injuryAdjustment("H","A",[{playerId:"a",name:"a",team:"H",status:"out",reportedAt:null},{playerId:"b",name:"b",team:"H",status:"out",reportedAt:null}],big).home,10);
});
test("CLV and market report use only games with captured lines",()=>{
 const r=marketReport([
  {projectedMargin:6,homeWinProbability:0.7,openSpread:-3,closeSpread:-4.5,closeHomeProb:0.64,finalHome:110,finalAway:100},
  {projectedMargin:-2,homeWinProbability:0.4,openSpread:-3,closeSpread:-2,closeHomeProb:0.57,finalHome:100,finalAway:104},
  {projectedMargin:1,homeWinProbability:0.53,openSpread:null,closeSpread:null,closeHomeProb:null,finalHome:99,finalAway:98}]);
 assert.equal(r.games,3);assert.equal(r.withClose,2);
 assert.equal(r.clv.games,2);assert.equal(r.clv.avgPoints,1.25);assert.equal(r.clv.beatClose,1);
 assert.equal(r.atsClose.wins,2);assert.equal(r.atsClose.losses,0);
 assert.equal(r.brier.games,2);
});
test("Platt scaling fits a monotone, calibrated curve and refuses tiny samples",()=>{
 assert.equal(fitPlatt([{margin:1,won:1}]),null);
 let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
 const pairs=[];for(let i=0;i<3000;i++){const m=(rnd()-0.5)*30;const p=1/(1+Math.exp(-(0.15*m+0.2)));pairs.push({margin:m,won:rnd()<p?1:0});}
 const f=fitPlatt(pairs);
 assert.ok(Math.abs(f.a-0.15)<0.03,String(f.a));assert.ok(Math.abs(f.b-0.2)<0.15,String(f.b));
 assert.ok(plattProbability(f,10)>plattProbability(f,0));
});
import {runBacktest} from "../lib/engine/backtest.ts";
test("backtest reports Platt scores and walk-forward ensemble weights on the same games",()=>{
 const teams="ABCDEFGH".split(""),str=Object.fromEntries(teams.map((t,i)=>[t,(4-i)*2]));
 let seed=11;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
 const rows=[];const start=Date.parse("2024-11-01T00:00:00Z");
 for(let d=0;d<150;d++)for(let k=0;k<4;k++){
  const h=teams[Math.floor(rnd()*8)];let a=teams[Math.floor(rnd()*8)];if(a===h)a=teams[(teams.indexOf(h)+1)%8];
  const m=Math.round(str[h]-str[a]+3+(rnd()-0.5)*24);const hs=110+Math.max(m,0),as=110+Math.max(-m,0)+(m===0?1:0);
  const date=new Date(start+d*86400000+k*3600000).toISOString();
  rows.push({date,team:h,opponent:a,teamScore:hs,opponentScore:as,location:"home"},{date,team:a,opponent:h,teamScore:as,opponentScore:hs,location:"away"});
 }
 const r=runBacktest(rows,"NBA",new Date("2025-04-01T00:00:00Z"),{maxWeeks:16,minTrainGames:60});
 const ew=r.models.find(m=>m.model==="ensemble-w");
 assert.ok(ew,"ensemble-w evaluated");assert.equal(ew.summary.games,r.evaluatedGames);
 assert.ok(ew.weights&&Math.abs(Object.values(ew.weights).reduce((s,x)=>s+x,0)-1)<1e-3);
 for(const m of r.models)assert.ok("platt" in m,m.model);
});
