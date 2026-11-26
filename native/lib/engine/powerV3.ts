import type {TeamGame} from "../ratings";
import {computePowerBoard,type CompletedGame} from "../powerRatings.ts";
import {SPORT_CONFIG} from "../sports.ts";
import type {EngineSport} from "./models";
import {V3_SETTINGS,buildSchedule,restDays,seasonOf,seasonStart,type Schedule} from "./v3.ts";

/**
 * Rounders Power Index v3 (challenger). power-v2 plus two documented refinements:
 *  1. Season prior: each team starts the season pulled toward last season's final power
 *     rating (regressed by the sport's v3 retention). The pull is worth PRIOR_GAMES games
 *     on opening day and fades with the sport's recency half-life, so it matters most in
 *     November college basketball and early NFL weeks and almost not at all by February.
 *  2. Rest: points per day of rest difference, estimated from the training residuals
 *     (ridge-shrunk toward 0), as in rounders-v3. Uses schedule dates only.
 * Settings are fixed in advance, not tuned on the evaluation window. Whether v3 beats v2 is
 * decided by the walk-forward backtest and the promotion gate, not assumed.
 */
export const POWER_V3_PRIOR_GAMES:Record<EngineSport,number>={NBA:8,NFL:3,NCAAM:6,NCAAF:3,NHL:10,MLB:20};
const DAY=86400000;
const homeRows=(games:CompletedGame[]):TeamGame[]=>games.map(g=>({
 date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,location:g.neutral?"neutral" as const:"home" as const}));

const priorCache=new Map<string,Map<string,number>>();
function seasonPrior(games:CompletedGame[],sport:EngineSport,season:number):Map<string,number>|null{
 const start=seasonStart(season,sport);
 const before=games.filter(g=>Date.parse(g.date)<start);
 if(before.length<50)return null;
 const key=`${sport}:${season}:${before.length}:${before[before.length-1].date}`;
 const hit=priorCache.get(key);if(hit)return hit;
 const keep=V3_SETTINGS[sport].retention;
 const board=computePowerBoard(homeRows(before),sport,new Date(start-1));
 const prior=new Map(board.rankings.map(r=>[r.team,r.rating*keep]));
 if(priorCache.size>32)priorCache.clear();
 priorCache.set(key,prior);
 return prior;
}
export type PowerV3Fit={predict(home:string,away:string,neutral:boolean,date?:string):number|null;priorWeight:number;restPointsPerDay:number};
export function fitPowerV3(history:CompletedGame[],sport:EngineSport,asOf:Date,schedule?:Schedule):PowerV3Fit{
 const cutoff=asOf.getTime();
 const games=history.filter(g=>Date.parse(g.date)<cutoff);
 const season=seasonOf(cutoff,sport),start=seasonStart(season,sport);
 const prior=seasonPrior(games,sport,season);
 const halfLife=SPORT_CONFIG[sport].power.halfLifeDays;
 const priorWeight=prior?POWER_V3_PRIOR_GAMES[sport]*Math.pow(0.5,Math.max(0,cutoff-start)/DAY/halfLife):0;
 const board=computePowerBoard(homeRows(games),sport,new Date(cutoff-1),prior&&priorWeight>0.01?{ratings:prior,weight:priorWeight}:undefined);
 const r=new Map(board.rankings.map(x=>[x.team,x.rating])),hfa=board.parameters.homeAdvantage;
 const cfg=V3_SETTINGS[sport],sched=schedule??buildSchedule(games);
 let sxy=0,sxx=0;
 for(const g of games){
  const t=Date.parse(g.date);
  const rh=restDays(sched,g.home,t,cfg.restCapDays),ra=restDays(sched,g.away,t,cfg.restCapDays);
  const h=r.get(g.home),a=r.get(g.away);
  if(rh===null||ra===null||h===undefined||a===undefined)continue;
  const x=rh-ra;if(x===0)continue;
  const res=(g.homeScore-g.awayScore)-(h-a+(g.neutral?0:hfa));
  const w=Math.pow(0.5,(cutoff-t)/DAY/365);
  sxy+=w*x*res;sxx+=w*x*x;
 }
 const beta=sxx>0?sxy/(sxx+cfg.restRidge):0;
 return {priorWeight:Number(priorWeight.toFixed(3)),restPointsPerDay:Number(beta.toFixed(4)),
  predict(home,away,neutral,date){
   const h=r.get(home),a=r.get(away);
   if(h===undefined||a===undefined)return null;
   let m=h-a+(neutral?0:hfa);
   if(date){const t=Date.parse(date);
    const rh=restDays(sched,home,t,cfg.restCapDays),ra=restDays(sched,away,t,cfg.restCapDays);
    if(rh!==null&&ra!==null)m+=beta*(rh-ra);}
   return m;
  }};
}
