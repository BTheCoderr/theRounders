import type {TeamGame} from "../ratings";
import {buildRatings,projectMatchup} from "../ratings.ts";
import {computePowerBoard,type CompletedGame} from "../powerRatings.ts";
import {fitResearchRpi} from "../researchRpi.ts";
import {fitElo,fitMasseyRidge} from "../walkForward.ts";
import {fitV3,type Schedule} from "./v3.ts";
import {fitPowerV3} from "./powerV3.ts";

/** NBA, NFL, college basketball and football, NHL and MLB (settings in lib/sports.ts). */
import {ALL_SPORTS,SPORT_CONFIG,isSport,type Sport} from "../sports.ts";
export type EngineSport=Sport;
export const ENGINE_SPORTS:readonly EngineSport[]=ALL_SPORTS;
export const isEngineSport=isSport;

/** Bump when the shared engine pipeline (totals, probability mapping, inputs) changes. */
export const ENGINE_REVISION="engine-2";   // engine-2: win probability σ calibrated from out-of-sample errors

export type ModelId="home-baseline"|"elo-margin"|"massey-ridge"|"rounders-v1"|"power-v2"|"rpi-v2.1"|"rounders-v3"|"ensemble"|"ensemble-w"|"power-v3";
/** Candidates that can be champion. Baselines are benchmarks only. */
export const CANDIDATE_MODELS:readonly ModelId[]=["rounders-v1","power-v2","rpi-v2.1","rounders-v3","ensemble","power-v3"];
export const BENCHMARK_MODELS:readonly ModelId[]=["home-baseline","elo-margin","massey-ridge"];
/**
 * Backtest-only challengers: evaluated walk-forward and through the promotion gate, but not
 * snapshotted live until wired in (their weights come from earlier out-of-sample errors).
 */
export const BACKTEST_CHALLENGERS:readonly ModelId[]=["ensemble-w"];
export const ALL_MODELS:readonly ModelId[]=[...BENCHMARK_MODELS,...CANDIDATE_MODELS,...BACKTEST_CHALLENGERS];
/** Members of both ensembles. */
export const ENSEMBLE_MEMBERS:readonly ModelId[]=["power-v2","rpi-v2.1","elo-margin","rounders-v3"];
export const MODEL_LABELS:Record<ModelId,string>={
 "home-baseline":"Home-advantage baseline",
 "elo-margin":"Elo (benchmark)",
 "massey-ridge":"Least-squares ridge (benchmark)",
 "rounders-v1":"Rounders v1",
 "power-v2":"Rounders Power Index v2",
 "rpi-v2.1":"Research RPI v2.1",
 "rounders-v3":"Rounders v3",
 "ensemble":"Rounders Ensemble",
 "ensemble-w":"Weighted Ensemble (challenger)",
 "power-v3":"Rounders Power Index v3 (challenger)"
};
export const isModelId=(s:string):s is ModelId=>(ALL_MODELS as readonly string[]).includes(s);

/** Fixed, documented sport settings. Not tuned on the evaluation window. */
export const SPORT_SETTINGS=Object.fromEntries(Object.entries(SPORT_CONFIG).map(([s,c])=>[s,{homeAdvantage:c.homeAdvantage,eloPointScale:c.eloPointScale,v1Baseline:c.v1Baseline,marginSigma:c.marginSigma}])) as Record<EngineSport,{homeAdvantage:number;eloPointScale:number;v1Baseline:number;marginSigma:number}>;

/** Returns the projected home-minus-away margin, or null when a team has no history. */
/** `date` (scheduled start) lets schedule-aware models use rest days; results are never needed. */
export type MarginPredictor=(home:string,away:string,neutral:boolean,date?:string)=>number|null;

const bothSides=(games:CompletedGame[]):TeamGame[]=>games.flatMap(g=>[
 {date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,location:g.neutral?"neutral" as const:"home" as const},
 {date:g.date,team:g.away,opponent:g.home,teamScore:g.awayScore,opponentScore:g.homeScore,location:g.neutral?"neutral" as const:"away" as const}
]);
const homeRows=(games:CompletedGame[]):TeamGame[]=>games.map(g=>({
 date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,
 location:g.neutral?"neutral" as const:"home" as const
}));

/**
 * Fit one model on games that finished strictly before `asOf`.
 * Callers must pass only past games; this function also refuses later ones.
 */
export function fitMarginModel(model:ModelId,history:CompletedGame[],sport:EngineSport,asOf:Date,schedule?:Schedule):MarginPredictor{
 const cutoff=asOf.getTime();
 const games=history.filter(g=>Date.parse(g.date)<cutoff);
 const s=SPORT_SETTINGS[sport];
 const known=new Set(games.flatMap(g=>[g.home,g.away]));
 const hfa=(neutral:boolean)=>neutral?0:s.homeAdvantage;
 switch(model){
  case "home-baseline":
   return (home,away,neutral)=>known.has(home)&&known.has(away)?hfa(neutral):null;
  case "elo-margin":{
   const elo=fitElo(games,s.eloPointScale,s.homeAdvantage);
   return (home,away,neutral)=>{
    const h=elo.get(home),a=elo.get(away);
    return h===undefined||a===undefined?null:(h-a)*s.eloPointScale+hfa(neutral);
   };
  }
  case "massey-ridge":{
   const r=fitMasseyRidge(games,s.homeAdvantage);
   return (home,away,neutral)=>{
    const h=r.get(home),a=r.get(away);
    return h===undefined||a===undefined?null:h-a+hfa(neutral);
   };
  }
  case "rounders-v1":{
   // Exactly what the market board has shown customers: projected home minus away score.
   const ratings=buildRatings(bothSides(games));
   return (home,away,neutral)=>{
    const p=projectMatchup(ratings,away,home,s.v1Baseline,hfa(neutral));
    return p?p.projectedHome-p.projectedAway:null;
   };
  }
  case "power-v2":{
   const board=computePowerBoard(homeRows(games),sport,new Date(cutoff-1));
   const r=new Map(board.rankings.map(x=>[x.team,x.rating]));
   return (home,away,neutral)=>{
    const h=r.get(home),a=r.get(away);
    return h===undefined||a===undefined?null:h-a+(neutral?0:board.parameters.homeAdvantage);
   };
  }
  case "power-v3":{
   const f=fitPowerV3(games,sport,asOf,schedule);
   return (home,away,neutral,date)=>f.predict(home,away,neutral,date);
  }
  case "rounders-v3":{
   const v3=fitV3(games,sport,asOf,schedule);
   return (home,away,neutral,date)=>v3.predict(home,away,neutral,date);
  }
  // Outside the walk-forward loop there are no out-of-sample weights yet: equal weights.
  case "ensemble-w":
  case "ensemble":{
   // Equal-weight average of the strongest independent fits; null unless every member covers the game.
   const members=(["power-v2","rpi-v2.1","elo-margin","rounders-v3"] as const).map(m=>fitMarginModel(m,games,sport,asOf,schedule));
   return (home,away,neutral,date)=>{
    let sum=0;
    for(const f of members){const v=f(home,away,neutral,date);if(v===null||!Number.isFinite(v))return null;sum+=v;}
    return sum/members.length;
   };
  }
  case "rpi-v2.1":{
   const fit=fitResearchRpi(homeRows(games),sport,asOf);
   return (home,away,neutral)=>{
    const h=fit.ratings.get(home),a=fit.ratings.get(away);
    return h===undefined||a===undefined?null:h-a+(neutral?0:fit.homeAdvantage);
   };
  }
 }
}
