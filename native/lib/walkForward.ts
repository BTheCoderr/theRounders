import type {TeamGame} from "./ratings";
import {computePowerBoard,uniqueCompletedGames,type CompletedGame,type Sport} from "./powerRatings";

/**
 * Historical-only expanding-window benchmark, recomputed at each UTC Monday.
 * The entire upcoming week stays out-of-sample; no within-week result is ever
 * consumed until the next week's model fitting.
 * All compared models use identical eligible games.
 */
export type Competitor="home-baseline"|"massey-ridge"|"elo-margin"|"rounders-power-v2";
export type CompetitorScore={
 model:Competitor;games:number;mae:number|null;winnerAccuracy:number|null;
 correctWinners:number;decidedGames:number;meanBias:number|null;
};
export type WalkForwardReport={
 method:"weekly-expanding-origin-v1";
 sport:Sport;
 totalHistoricalGames:number;
 historySeasons:number[];
 evaluatedWeeks:number;
 evaluatedGames:number;
 excludedColdStart:number;
 from:string|null;
 through:string|null;
 models:CompetitorScore[];
 bestByMAE:Competitor|null;
 betterThanBaseline:boolean|null;
 warning:string;
};

const settings:Record<Sport,{hfa:number;eloPointScale:number}> = {
 NBA:{hfa:2.2,eloPointScale:0.04},
 NFL:{hfa:2.2,eloPointScale:0.03},
 NHL:{hfa:0.18,eloPointScale:0.0035},
 MLB:{hfa:0.25,eloPointScale:0.005}
};
const competitors:Competitor[]=["home-baseline","massey-ridge","elo-margin","rounders-power-v2"];
const week=7*86400000;
const round=(n:number)=>Number(n.toFixed(3));
const weekStart=(timestamp:number)=>{const d=new Date(timestamp);const utcDay=d.getUTCDay();return Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),d.getUTCDate())-((utcDay+6)%7)*86400000;};
const toRows=(games:CompletedGame[]):TeamGame[]=>games.map(g=>({
 date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,
 location:g.neutral?"neutral":"home"
}));

/** Equal-weight, ridge-regularized least squares of score margins (simple Massey-style comparator). */
export function fitMasseyRidge(games:CompletedGame[],hfa:number):Map<string,number>{
 const teams=[...new Set(games.flatMap(g=>[g.home,g.away]))].sort();
 const index=new Map(teams.map((t,i)=>[t,i]));
 const n=teams.length;
 const rhs=Array<number>(n).fill(0);
 const diagonal=Array<number>(n).fill(1.25);
 const edges: Array<{h:number;a:number}>=[];
 for(const g of games){
  const h=index.get(g.home)!,a=index.get(g.away)!;
  const target=g.homeScore-g.awayScore-(g.neutral?0:hfa);
  rhs[h]+=target;rhs[a]-=target;diagonal[h]++;diagonal[a]++;
  edges.push({h,a});
 }
 const values=Array<number>(n).fill(0);
 // Jacobi iteration, damped to avoid the 2-team bipartite oscillation.
 for(let k=0;k<120;k++){
  const adjacency=Array<number>(n).fill(0);
  for(const e of edges){adjacency[e.h]+=values[e.a];adjacency[e.a]+=values[e.h]}
  for(let i=0;i<n;i++)values[i]=0.5*values[i]+0.5*(rhs[i]+adjacency[i])/diagonal[i];
 }
 const center=n?values.reduce((a,b)=>a+b,0)/n:0;
 return new Map(teams.map((t,i)=>[t,values[i]-center]));
}

/** Ordinary pregame Elo, no margin-of-victory hindsight in predictions. */
export function fitElo(games:CompletedGame[],homePointScale:number,hfa:number):Map<string,number>{
 const ratings=new Map<string,number>();
 for(const g of games){
  const home=ratings.get(g.home)??1500;
  const away=ratings.get(g.away)??1500;
  const advantage=(g.neutral?0:hfa)/homePointScale;
  const expectation=1/(1+10**(-(home-away+advantage)/400));
  const actual=g.homeScore===g.awayScore?0.5:g.homeScore>g.awayScore?1:0;
  const update=20*(actual-expectation);
  ratings.set(g.home,home+update);
  ratings.set(g.away,away-update);
 }
 return ratings;
}
type Accumulator={sumError:number;sumBias:number;games:number;correct:number;decided:number};
const initial=():Accumulator=>({sumError:0,sumBias:0,games:0,correct:0,decided:0});
export function compareWalkForward(rows:TeamGame[],sport:Sport,asOf=new Date(),maxWeeks=52):WalkForwardReport{
 const params=settings[sport];
 if(!params)throw new Error("Unsupported sport");
 if(!(maxWeeks>=1&&maxWeeks<=156&&Number.isInteger(maxWeeks)))throw new Error("Invalid evaluation window");
 const history=uniqueCompletedGames(rows,asOf);
 const seasons=[...new Set(history.map(g=>g.date.slice(0,4)))].map(Number).sort((a,b)=>a-b);
 const output=new Map(competitors.map(name=>[name,initial()]));
 const groups=new Map<number,CompletedGame[]>();
 for(const game of history){
  const key=weekStart(Date.parse(game.date));
  groups.set(key,[...(groups.get(key)||[]),game]);
 }
 const weeks=[...groups.keys()].sort((a,b)=>a-b);
 let weeksEvaluated=0,excludedColdStart=0;
 let start:string|null=null,end:string|null=null;
 const selected=weeks.slice(-maxWeeks);
 for(const origin of selected){
  const train=history.filter(g=>Date.parse(g.date)<origin);
  const upcoming=groups.get(origin)||[];
  if(train.length<30){excludedColdStart+=upcoming.length;continue}
  const power=computePowerBoard(toRows(train),sport,new Date(origin));
  const powerRating=new Map(power.rankings.map(r=>[r.team,r.rating]));
  const massey=fitMasseyRidge(train,params.hfa);
  const elo=fitElo(train,params.eloPointScale,params.hfa);
  const eligible=upcoming.filter(g=>powerRating.has(g.home)&&powerRating.has(g.away)
   &&massey.has(g.home)&&massey.has(g.away)&&elo.has(g.home)&&elo.has(g.away));
  if(!eligible.length){excludedColdStart+=upcoming.length;continue}
  excludedColdStart+=upcoming.length-eligible.length;
  weeksEvaluated++;
  if(!start)start=eligible[0].date;
  end=eligible[eligible.length-1].date;
  for(const game of eligible){
   const home=game.home,away=game.away;
   const hfa=game.neutral?0:params.hfa;
   const predictions:Record<Competitor,number>={
    "home-baseline":hfa,
    "massey-ridge":(massey.get(home)!-massey.get(away)!)+hfa,
    "elo-margin":(elo.get(home)!-elo.get(away)!)*params.eloPointScale+hfa,
    "rounders-power-v2":(powerRating.get(home)!-powerRating.get(away)!)+hfa
   };
   const actual=game.homeScore-game.awayScore;
   for(const model of competitors){
    const entry=output.get(model)!;
    const forecast=predictions[model];
    entry.sumError+=Math.abs(forecast-actual);
    entry.sumBias+=forecast-actual;
    entry.games++;
    // Ties are omitted from straight-up winner accuracy only, not MAE.
    if(actual!==0){
     entry.decided++;
     if((forecast>0&&actual>0)||(forecast<0&&actual<0))entry.correct++;
    }
   }
  }
 }
 const models=competitors.map(model=>{
  const entry=output.get(model)!;
  return{model,games:entry.games,mae:entry.games?round(entry.sumError/entry.games):null,
   winnerAccuracy:entry.decided?round(entry.correct/entry.decided*100):null,
   correctWinners:entry.correct,decidedGames:entry.decided,
   meanBias:entry.games?round(entry.sumBias/entry.games):null};
 });
 const num=models[0].games;
 const best=num?models.reduce((a,b)=>b.mae!==null&&a.mae!==null&&b.mae<a.mae?b:a).model:null;
 const base=models[0].mae,rounders=models[3].mae;
 const valid=num>=25&&weeksEvaluated>=4;
 return {
  method:"weekly-expanding-origin-v1",sport,totalHistoricalGames:history.length,historySeasons:seasons,
  evaluatedWeeks:weeksEvaluated,evaluatedGames:num,excludedColdStart,from:start,through:end,models,
  bestByMAE:valid?best:null,
  betterThanBaseline:valid&&base!==null&&rounders!==null?rounders<base:null,
  warning:!valid?"Insufficient eligible historical games for a reliable ranking of these comparators.":
    seasons.length<2?"Diagnostic only: fewer than two calendar years represented; multi-season superiority is NOT established.":
    "Historical weekly walk-forward comparison, fixed untuned parameters; results are not independently validated or guaranteed to generalize."
 };
}
