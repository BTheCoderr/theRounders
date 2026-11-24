import test from "node:test";
import assert from "node:assert/strict";
import {fitMarginModel,ALL_MODELS,CANDIDATE_MODELS} from "../lib/engine/models.ts";
import {fitTotals,leagueAverageTotal} from "../lib/engine/totals.ts";
import {normalCdf,winProbability,summarizeForecasts} from "../lib/engine/metrics.ts";
import {runBacktest} from "../lib/engine/backtest.ts";
import {evaluatePromotion,championFor,MIN_GATE_GAMES} from "../lib/engine/promotion.ts";
import {predictUpcoming,gradePrediction,snapshotWindow} from "../lib/engine/predict.ts";
import {parseUpcoming,parseFinals} from "../lib/results/espnSchedule.ts";
import {consensusLine,teamKey} from "../lib/engine/market.ts";
import {uniqueCompletedGames} from "../lib/powerRatings.ts";

// Synthetic league: 8 teams with fixed strengths, deterministic noise, games every 2 days.
const TEAMS=["A","B","C","D","E","F","G","H"];
const STRENGTH={A:8,B:5,C:3,D:1,E:-1,F:-3,G:-5,H:-8};
const OFFENSE={A:4,B:1,C:3,D:0,E:-1,F:2,G:-2,H:-3};
function league(days=400,start=Date.UTC(2023,9,1),sport="NBA"){
 const rows=[];const base=sport==="NFL"?22:110;let k=0;
 for(let d=0;d<days;d+=2){
  for(let i=0;i<TEAMS.length;i+=2){
   const shift=(d/2)%7+1;
   const home=TEAMS[i],away=TEAMS[(i+shift)%TEAMS.length];
   if(home===away)continue;
   const noise=((k*37)%13)-6;k++;
   const margin=STRENGTH[home]-STRENGTH[away]+2+noise;
   const total=2*base+OFFENSE[home]+OFFENSE[away]+(((k*11)%9)-4);
   const hs=Math.round((total+margin)/2),as=Math.round((total-margin)/2);
   rows.push({date:new Date(start+d*86400000).toISOString(),team:home,opponent:away,teamScore:hs,opponentScore:as,location:"home"});
  }
 }
 return rows;
}
const asOf=new Date(Date.UTC(2024,10,1));

test("normal CDF and win probability behave sensibly",()=>{
 assert.ok(Math.abs(normalCdf(0)-0.5)<1e-7);
 assert.ok(Math.abs(normalCdf(1.96)-0.975)<1e-3);
 assert.ok(winProbability(6,12)>0.68&&winProbability(6,12)<0.7);
 assert.equal(winProbability(-200,12),0.005);
 assert.throws(()=>winProbability(NaN,12));
});

test("every model ignores games that finish after the fit time",()=>{
 const rows=league();
 const games=uniqueCompletedGames(rows,new Date("2030-01-01"));
 const cut=new Date(Date.UTC(2024,5,1));
 const future=[...games,{date:"2024-06-02T00:00:00.000Z",home:"H",away:"A",homeScore:200,awayScore:0,neutral:false}];
 for(const m of ALL_MODELS){
  const a=fitMarginModel(m,games,"NBA",cut)("A","H",false);
  const b=fitMarginModel(m,future,"NBA",cut)("A","H",false);
  assert.equal(a,b,m);
 }
});

test("candidate models rank the strong team above the weak team",()=>{
 const games=uniqueCompletedGames(league(),asOf);
 for(const m of CANDIDATE_MODELS){
  const margin=fitMarginModel(m,games,"NBA",asOf)("A","H",true);
  assert.ok(margin>5,m+" "+margin);
 }
});

test("totals model learns offense and beats nothing it should not",()=>{
 const games=uniqueCompletedGames(league(),asOf);
 const fit=fitTotals(games,"NBA",asOf);
 const high=fit.predict("A","C",true),low=fit.predict("H","G",true);
 assert.ok(high.total>low.total+5);
 assert.equal(fit.predict("A","Z",false),null);
 assert.ok(Math.abs(leagueAverageTotal(games,"NBA",asOf)-220)<6);
});

test("backtest scores all models on identical games and is unaffected by later results",()=>{
 const rows=league();
 const r=runBacktest(rows,"NBA",asOf,{maxWeeks:30,minTrainGames:60});
 assert.ok(r.evaluatedGames>50);
 for(const m of r.models)assert.equal(m.summary.games,r.evaluatedGames,m.model);
 for(const m of ALL_MODELS)assert.equal(r.paired[m].length,r.evaluatedGames);
 const extra=[...rows,{date:"2025-06-01T00:00:00Z",team:"H",opponent:"A",teamScore:300,opponentScore:0,location:"home"}];
 const again=runBacktest(extra,"NBA",asOf,{maxWeeks:30,minTrainGames:60});
 assert.deepEqual(again.models,r.models);
 const base=r.models.find(m=>m.model==="home-baseline").summary.marginMAE;
 const power=r.models.find(m=>m.model==="power-v2").summary.marginMAE;
 assert.ok(power<base,"a real signal should beat the home-only baseline on synthetic data");
 assert.ok(r.totals.summary.mae<r.totals.baseline.mae);
});

test("promotion gate refuses small samples and single seasons",()=>{
 const r=runBacktest(league(),"NBA",asOf,{maxWeeks:30,minTrainGames:60});
 const d=evaluatePromotion(r,"rounders-v1","power-v2");
 assert.equal(d.recommend,false);
 assert.ok(d.reasons.some(x=>/needs/.test(x)));
 assert.equal(evaluatePromotion(r,"rounders-v1","home-baseline").recommend,false);
});

test("promotion gate recommends a clearly better challenger with enough evidence",()=>{
 const n=MIN_GATE_GAMES.NBA+50;
 const champ=Array.from({length:n},(_,i)=>10+(i%5)),chall=champ.map((x,i)=>x-2+((i%3)-1)*0.1);
 const report={sport:"NBA",seasons:[2023,2024],paired:{"rounders-v1":champ,"power-v2":chall},
  pairedBrier:{"rounders-v1":champ.map(()=>0.22),"power-v2":chall.map(()=>0.21)}};
 const d=evaluatePromotion(report,"rounders-v1","power-v2");
 assert.equal(d.recommend,true,d.reasons.join(" "));
 const worseBrier={...report,pairedBrier:{"rounders-v1":champ.map(()=>0.2),"power-v2":chall.map(()=>0.25)}};
 assert.equal(evaluatePromotion(worseBrier,"rounders-v1","power-v2").recommend,false);
});

test("champion defaults follow the gate and only accept candidate models",()=>{
 assert.equal(championFor("NBA",{}),"power-v2");assert.equal(championFor("NFL",{}),"rounders-v1");
 assert.equal(championFor("NFL",{ROUNDERS_CHAMPION_NFL:"power-v2"}),"power-v2");
 assert.equal(championFor("NBA",{ROUNDERS_CHAMPION_NBA:"home-baseline"}),"power-v2");
});

test("snapshots are strictly pregame, use only past games, and stay internally consistent",()=>{
 const games=uniqueCompletedGames(league(),asOf);
 const now=new Date(Date.UTC(2024,10,1,15,20));
 const upcoming=[
  {eventId:"1",startsAt:new Date(now.getTime()+5*60000).toISOString(),season:2025,home:"A",away:"B",homeId:"1",awayId:"2",neutral:false},
  {eventId:"2",startsAt:new Date(now.getTime()+6*3600000).toISOString(),season:2025,home:"C",away:"H",homeId:"3",awayId:"8",neutral:false},
  {eventId:"3",startsAt:new Date(now.getTime()+7*3600000).toISOString(),season:2025,home:"C",away:"NEW",homeId:"3",awayId:"99",neutral:false}
 ];
 const rows=predictUpcoming(games,upcoming,"NBA",now,{dataSource:"test"});
 assert.equal(rows.length,CANDIDATE_MODELS.length,"skips the game inside the lead time and the unknown team");
 for(const r of rows){
  assert.equal(r.provider_event_id,"2");
  assert.ok(Date.parse(r.predicted_at)<Date.parse(r.starts_at));
  assert.ok(Date.parse(r.training_through)<Date.parse(r.predicted_at));
  assert.ok(Math.abs(r.projected_home+r.projected_away-r.projected_total)<0.02);
  assert.ok(Math.abs(r.projected_home-r.projected_away-r.projected_margin)<0.02);
  assert.equal(r.projected_winner,r.home_win_probability>=0.5?"C":"H");
  assert.match(r.model_version,/@engine-1$/);
 }
});

test("grading computes errors and leaves ties out of winner accuracy",()=>{
 const p={projected_margin:4,projected_total:220,home_win_probability:0.63};
 assert.deepEqual(gradePrediction(p,112,105),{final_home:112,final_away:105,winner_correct:true,brier:0.1369,margin_error:-3,total_error:3});
 const tie=gradePrediction({projected_margin:-1,projected_total:40,home_win_probability:0.47},20,20);
 assert.equal(tie.winner_correct,null);assert.equal(tie.brier,null);
});

test("summary reports accuracy, Brier, calibration, spread and total records",()=>{
 const s=summarizeForecasts([
  {homeWinProbability:0.7,projectedMargin:5,projectedTotal:220,homeScore:110,awayScore:100,marketSpreadHome:-3,marketTotal:215},
  {homeWinProbability:0.6,projectedMargin:2,projectedTotal:210,homeScore:100,awayScore:104,marketSpreadHome:-1,marketTotal:212},
  {homeWinProbability:0.2,projectedMargin:-8,projectedTotal:200,homeScore:90,awayScore:99,marketSpreadHome:null,marketTotal:null}
 ]);
 assert.equal(s.games,3);assert.equal(s.winnerAccuracy,0.6667);
 assert.equal(s.brierScore,Number(((0.09+0.36+0.04)/3).toFixed(4)));
 assert.deepEqual(s.againstSpread,{games:2,wins:1,losses:1,pushes:0,winRate:0.5});
 assert.deepEqual(s.againstTotal,{games:2,wins:1,losses:1,pushes:0,winRate:0.5});
 assert.equal(s.calibration.reduce((n,b)=>n+b.forecasts,0),3);
 assert.equal(summarizeForecasts([]).brierScore,null);
});

test("schedule parser keeps only scheduled regular-season games with IDs",()=>{
 const from=new Date("2026-11-23T12:00:00Z"),to=new Date("2026-11-24T14:00:00Z");
 const ev=(id,state,type,date,h="1",a="2")=>({id,date,season:{type,year:2027},status:{type:{state,completed:state==="post"}},
  competitions:[{competitors:[{homeAway:"home",team:{id:h,displayName:"Home "+h}},{homeAway:"away",team:{id:a,displayName:"Away "+a}}]}]});
 const out=parseUpcoming([ev("10","pre",2,"2026-11-24T00:30Z"),ev("11","in",2,"2026-11-24T00:30Z"),ev("12","pre",1,"2026-11-24T00:30Z"),
  ev("13","pre",2,"2026-11-25T00:30Z"),ev("14","pre",2,"2026-11-24T01:00Z","3","3"),ev("10","pre",2,"2026-11-24T00:30Z")],from,to);
 assert.deepEqual(out.map(x=>x.eventId),["10"]);
 const finals=parseFinals([{id:"9",status:{type:{state:"post",completed:true}},competitions:[{competitors:[
  {homeAway:"home",score:"101",team:{id:"1"}},{homeAway:"away",score:"99",team:{id:"2"}}]}]}]);
 assert.deepEqual(finals.get("9"),{eventId:"9",homeId:"1",awayId:"2",homeScore:101,awayScore:99});
});

test("market consensus uses live quotes only and matches LA team names",()=>{
 assert.equal(teamKey("LA Clippers"),teamKey("Los Angeles Clippers"));
 const q=(state,book,market,selection,line)=>({eventId:"e",sport:"NBA",market,selection,line,price:-110,book,updatedAt:"",state,away:"Boston Celtics",home:"Los Angeles Clippers",startTime:""});
 const quotes=[q("live","A","spread","Los Angeles Clippers",-2.5),q("live","B","spread","Los Angeles Clippers",-3.5),q("live","C","spread","Los Angeles Clippers",-3),
  q("live","A","total","Over",221.5),q("simulated","Z","spread","Los Angeles Clippers",-20)];
 assert.deepEqual(consensusLine(quotes,"LA Clippers","Boston Celtics"),{spreadHome:-3,total:221.5,books:3});
 assert.deepEqual(consensusLine(quotes.filter(x=>x.state==="simulated"),"LA Clippers","Boston Celtics"),{spreadHome:null,total:null,books:0});
});

test("snapshot windows: NBA about a day, NFL a week on Tuesdays",()=>{
 const hours=(w)=>(w.to-w.from)/3600000;
 assert.equal(hours(snapshotWindow("NBA",new Date("2026-11-24T15:20:00Z"))),26);
 assert.equal(hours(snapshotWindow("NFL",new Date("2026-11-24T15:25:00Z"))),168);
 assert.equal(hours(snapshotWindow("NFL",new Date("2026-11-26T15:25:00Z"))),48);
});

import {buildSchedule,restDays,fitV3,seasonOf} from "../lib/engine/v3.ts";
test("rest days come from the schedule, ignore offseason gaps, and are capped",()=>{
 const s=buildSchedule([{date:"2025-01-01T00:00:00Z",home:"A",away:"B"},{date:"2025-01-02T00:00:00Z",home:"A",away:"C"},{date:"2025-03-30T00:00:00Z",home:"B",away:"A"}]);
 assert.equal(restDays(s,"A",Date.parse("2025-01-02T00:00:00Z"),3),1);
 assert.equal(restDays(s,"B",Date.parse("2025-01-02T00:00:00Z"),3),1);
 assert.equal(restDays(s,"C",Date.parse("2025-01-02T00:00:00Z"),3),null,"first game in data");
 assert.equal(restDays(s,"A",Date.parse("2025-03-30T00:00:00Z"),3),null,"gap over 40 days is not rest");
 assert.equal(seasonOf(Date.parse("2025-10-21T00:00:00Z")),2025);assert.equal(seasonOf(Date.parse("2026-02-01T00:00:00Z")),2025);
});
test("v3 learns a rest effect from data and never uses later results",()=>{
 // Synthetic: equal teams, home team wins by 3 more points per extra day of rest.
 const teams=["A","B","C","D","E","F"],rows=[];let day=0,k=0;
 const start=Date.UTC(2024,9,1);
 // Two games a day among six teams, so rest differs between opponents.
 let seed=7;const rnd=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
 for(let r=0;r<240;r++){day+=1;const order=[...teams].sort(()=>rnd()-0.5);
  for(let i=0;i<2;i++){const h=order[i*2],a=order[i*2+1];k++;
   rows.push({date:new Date(start+day*86400000+i*1000).toISOString(),home:h,away:a,homeScore:100,awayScore:100,neutral:false});}}
 const sched=buildSchedule(rows);
 const withRest=rows.map(g=>{const t=Date.parse(g.date);const rh=restDays(sched,g.home,t,3),ra=restDays(sched,g.away,t,3);const m=2+(rh!==null&&ra!==null?3*(rh-ra):0)+((k++%5)-2);return {...g,homeScore:100+Math.max(0,m),awayScore:100+Math.max(0,-m)};});
 const asOf=new Date(start+(day-20)*86400000);
 const fit=fitV3(withRest,"NBA",asOf,sched);
 assert.ok(fit.restPointsPerDay>1.5&&fit.restPointsPerDay<3.5,String(fit.restPointsPerDay));
 const future=[...withRest,{date:new Date(asOf.getTime()+86400000).toISOString(),home:"A",away:"B",homeScore:300,awayScore:0,neutral:false}];
 assert.equal(fitV3(future,"NBA",asOf,sched).predict("A","B",false),fit.predict("A","B",false));
});
