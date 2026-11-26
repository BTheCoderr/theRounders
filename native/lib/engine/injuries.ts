/**
 * Player impact and the injury-adjusted Power Index v4 challenger.
 *
 * These are documented starting assumptions, not tuned results. v4 only becomes credible
 * after forward testing against the locked power-v2 picks on the same games; nothing here
 * claims an accuracy improvement.
 */
export const INJURY_MODEL="injury-v4";
export const INJURY_REVISION="injury-v4.0";

/** Probability a listed player misses the game, by report status (prior; refit once logged outcomes exist). */
export const STATUS_WEIGHT:Record<string,number>={
 "out":1,"out for season":1,"injured reserve":1,"ir":1,"suspended":1,"doubtful":0.8,
 "questionable":0.35,"day-to-day":0.25,"game time decision":0.4,"probable":0.1,"active":0
};
export function statusWeight(status:string):number{
 const s=status.trim().toLowerCase();
 if(s in STATUS_WEIGHT)return STATUS_WEIGHT[s];
 if(s.startsWith("out"))return 1;
 return 0;   // unknown statuses are ignored, never guessed
}

export type BoxRow={playerId:string;name:string;team:string;minutes:number;plusMinus:number};
export type Impact={playerId:string;name:string;team:string;games:number;mpg:number;impact:number;method:string};
/**
 * NBA v1: regressed on-court plus-minus per 48 minutes (shrunk toward a replacement-level
 * player with 1,000 phantom minutes), scaled by minutes per game. Result = team margin
 * points per game the player is worth over a replacement. Clamped to a sane range.
 */
export const NBA_IMPACT_METHOD="nba-pm-regressed-v1";
export function nbaImpacts(rows:readonly BoxRow[],opts={replacementPer48:-2,priorMinutes:1000,min:-2,max:8}):Impact[]{
 const by=new Map<string,{name:string;team:string;g:number;min:number;pm:number}>();
 for(const r of rows){
  if(!(r.minutes>0)||!Number.isFinite(r.plusMinus))continue;   // DNPs and bad rows don't count as games
  const e=by.get(r.playerId)||{name:r.name,team:r.team,g:0,min:0,pm:0};
  e.g++;e.min+=r.minutes;e.pm+=r.plusMinus;e.team=r.team;by.set(r.playerId,e);
 }
 const out:Impact[]=[];
 for(const [id,e] of by){
  const per48=(e.pm+opts.replacementPer48*opts.priorMinutes/48)/(e.min+opts.priorMinutes)*48;
  const mpg=e.min/e.g;
  const impact=Math.min(opts.max,Math.max(opts.min,(per48-opts.replacementPer48)*mpg/48));
  out.push({playerId:id,name:e.name,team:e.team,games:e.g,mpg:Number(mpg.toFixed(1)),impact:Number(impact.toFixed(2)),method:NBA_IMPACT_METHOD});
 }
 return out.sort((a,b)=>b.impact-a.impact);
}
/**
 * NFL v1: only the starting quarterback is modeled (largest documented single-player effect).
 * Starter = the team's QB with the most pass attempts this season. Prior: 4.5 points of margin
 * over the backup. Other positions are 0 until data supports them.
 */
export const NFL_IMPACT_METHOD="nfl-starting-qb-prior-v1";
export function nflImpacts(qbs:readonly {playerId:string;name:string;team:string;attempts:number;games:number}[],starterValue=4.5):Impact[]{
 const best=new Map<string,typeof qbs[number]>();
 for(const q of qbs)if(q.attempts>0&&(!best.has(q.team)||q.attempts>best.get(q.team)!.attempts))best.set(q.team,q);
 return [...best.values()].map(q=>({playerId:q.playerId,name:q.name,team:q.team,games:q.games,mpg:0,impact:starterValue,method:NFL_IMPACT_METHOD}));
}

export type Listed={playerId:string;name:string;team:string;status:string;reportedAt:string|null};
export type Adjustment={home:number;away:number;net:number;players:Array<{playerId:string;name:string;team:string;status:string;weight:number;impact:number;expectedLoss:number;reportedAt:string|null}>};
/**
 * Expected margin points each team loses to listed absences: sum of impact x miss probability,
 * capped per team (a roster can only lose so much; replacements absorb the rest).
 * net > 0 favors the home team (the away side lost more).
 */
export function injuryAdjustment(home:string,away:string,listed:readonly Listed[],impacts:ReadonlyMap<string,Impact>,capPerTeam=10):Adjustment{
 const players:Adjustment["players"]=[];
 let h=0,a=0;
 for(const l of listed){
  if(l.team!==home&&l.team!==away)continue;
  const imp=impacts.get(l.playerId);const w=statusWeight(l.status);
  if(!imp||!(imp.impact>0)||!(w>0))continue;
  const loss=imp.impact*w;
  players.push({playerId:l.playerId,name:l.name,team:l.team,status:l.status,weight:w,impact:imp.impact,expectedLoss:Number(loss.toFixed(2)),reportedAt:l.reportedAt});
  if(l.team===home)h+=loss;else a+=loss;
 }
 h=Math.min(capPerTeam,h);a=Math.min(capPerTeam,a);
 return {home:Number(h.toFixed(2)),away:Number(a.toFixed(2)),net:Number((a-h).toFixed(2)),players};
}
