import type {TeamGame} from "../ratings";
import type {CompletedGame} from "../powerRatings";
import {fitResearchRpi} from "../researchRpi.ts";
import type {EngineSport} from "./models";
import {SPORT_CONFIG,seasonFor} from "../sports.ts";

/**
 * Rounders v3 (Massey-style refinements on the research RPI fit):
 *  1. Season priors: each season starts from last season's final ratings,
 *     regressed halfway to average, instead of from zero.
 *  2. Rest: the effect of rest-day differences on the margin is estimated from
 *     the training residuals (back-to-backs in the NBA, byes and short weeks in the NFL).
 * Only completed games before the fit time are used. Game dates (the schedule)
 * are used for rest because schedules are published before games are played.
 */
const DAY=86400000;
export const V3_SETTINGS=Object.fromEntries(Object.entries(SPORT_CONFIG).map(([s,c])=>[s,c.v3])) as Record<EngineSport,{retention:number;restCapDays:number;restRidge:number}>;
/** Season label: the year the season began; MLB uses the calendar year. */
export const seasonOf=(t:number,sport?:EngineSport)=>seasonFor(sport,t);
const seasonStart=(season:number,sport?:EngineSport)=>sport&&SPORT_CONFIG[sport].calendarSeason?Date.UTC(season,0,1):Date.UTC(season,6,1);

/** Team -> sorted game timestamps, from schedule dates only (no results). */
export type Schedule=Map<string,number[]>;
export function buildSchedule(games:Array<{date:string;home:string;away:string}>):Schedule{
 const s:Schedule=new Map();
 for(const g of games){const t=Date.parse(g.date);if(!Number.isFinite(t))continue;
  for(const team of [g.home,g.away]){const list=s.get(team)||[];list.push(t);s.set(team,list);}}
 for(const list of s.values())list.sort((a,b)=>a-b);
 return s;
}
/** Days since the team's previous game, capped; null when unknown (first game of the data). */
export function restDays(schedule:Schedule,team:string,t:number,cap:number):number|null{
 const list=schedule.get(team);if(!list)return null;
 let lo=0,hi=list.length;
 while(lo<hi){const mid=(lo+hi)>>1;if(list[mid]<t-60000)lo=mid+1;else hi=mid;}   // last game strictly before t (1 min tolerance)
 if(lo===0)return null;
 const days=(t-list[lo-1])/DAY;
 return days>40?null:Math.min(cap,Math.max(0,days));   // offseason gaps are not rest
}
const homeRows=(games:CompletedGame[]):TeamGame[]=>games.map(g=>({
 date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,location:g.neutral?"neutral" as const:"home" as const
}));
const priorCache=new Map<string,Map<string,number>>();
/** Final ratings of every earlier season, fitted only on games before this season began. */
function seasonPrior(history:CompletedGame[],sport:EngineSport,season:number):Map<string,number>|undefined{
 const start=seasonStart(season,sport);
 const before=history.filter(g=>Date.parse(g.date)<start);
 if(before.length<50)return undefined;
 const key=`${sport}:${season}:${before.length}:${before[before.length-1].date}`;
 const hit=priorCache.get(key);if(hit)return hit;
 const prior=fitResearchRpi(homeRows(before),sport,new Date(start)).ratings;
 if(priorCache.size>32)priorCache.clear();
 priorCache.set(key,prior);
 return prior;
}
export type V3Fit={predict(home:string,away:string,neutral:boolean,date?:string):number|null;homeAdvantage:number;restPointsPerDay:number};
export function fitV3(history:CompletedGame[],sport:EngineSport,asOf:Date,schedule?:Schedule):V3Fit{
 const cfg=V3_SETTINGS[sport],cutoff=asOf.getTime();
 const games=history.filter(g=>Date.parse(g.date)<cutoff);
 const prior=seasonPrior(games,sport,seasonOf(cutoff,sport));
 const fit=fitResearchRpi(homeRows(games),sport,asOf,prior?{priorRatings:prior,priorRetention:cfg.retention}:{});
 const sched=schedule??buildSchedule(games);
 // Rest coefficient: ridge regression of training residuals on the rest-day difference.
 let sxy=0,sxx=0;
 for(const g of games){
  const t=Date.parse(g.date);
  const rh=restDays(sched,g.home,t,cfg.restCapDays),ra=restDays(sched,g.away,t,cfg.restCapDays);
  const h=fit.ratings.get(g.home),a=fit.ratings.get(g.away);
  if(rh===null||ra===null||h===undefined||a===undefined)continue;
  const x=rh-ra;if(x===0)continue;
  const r=(g.homeScore-g.awayScore)-(h-a+(g.neutral?0:fit.homeAdvantage));
  const w=Math.pow(0.5,(cutoff-t)/DAY/365);   // recent seasons count more
  sxy+=w*x*r;sxx+=w*x*x;
 }
 const beta=sxx>0?sxy/(sxx+cfg.restRidge):0;
 return {homeAdvantage:fit.homeAdvantage,restPointsPerDay:Number(beta.toFixed(4)),
  predict(home,away,neutral,date){
   const h=fit.ratings.get(home),a=fit.ratings.get(away);
   if(h===undefined||a===undefined)return null;
   let m=h-a+(neutral?0:fit.homeAdvantage);
   if(date){const t=Date.parse(date);
    const rh=restDays(sched,home,t,cfg.restCapDays),ra=restDays(sched,away,t,cfg.restCapDays);
    if(rh!==null&&ra!==null)m+=beta*(rh-ra);}
   return m;
  }};
}
