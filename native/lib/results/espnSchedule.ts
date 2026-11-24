import type {UpcomingGame} from "../engine/predict";

/** Upcoming regular-season games from ESPN's public scoreboard (unofficial; no license implied). */
import {SPORT_CONFIG,espnScoreboardUrl,mapLimit,type Sport} from "../sports.ts";
type Competitor={homeAway?:string;team?:{id?:string;displayName?:string;abbreviation?:string}};
type Event={
 id?:string;date?:string;season?:{type?:number|string;year?:number};
 status?:{type?:{state?:string;completed?:boolean;shortDetail?:string;detail?:string}};
 competitions?:Array<{neutralSite?:boolean;competitors?:Competitor[]}>;
};
const ymd=(d:Date)=>d.toISOString().slice(0,10).replace(/-/g,"");

/** Keep only scheduled (not started), regular-season games with stable IDs inside [from, to). */
export function parseUpcoming(events:Event[],from:Date,to:Date):UpcomingGame[]{
 const out:UpcomingGame[]=[],seen=new Set<string>();
 for(const e of events){
  if(e?.status?.type?.state!=="pre"||e.status.type.completed)continue;
  if(Number(e.season?.type)!==2)continue;
  const start=Date.parse(e.date||"");
  if(!Number.isFinite(start)||start<from.getTime()||start>=to.getTime())continue;
  const c=e.competitions?.[0];
  const home=c?.competitors?.find(x=>x.homeAway==="home"),away=c?.competitors?.find(x=>x.homeAway==="away");
  const homeId=String(home?.team?.id||"").trim(),awayId=String(away?.team?.id||"").trim();
  const hn=(home?.team?.displayName||"").trim(),an=(away?.team?.displayName||"").trim();
  const id=String(e.id||"").trim(),season=Number(e.season?.year);
  if(!id||!homeId||!awayId||homeId===awayId||!hn||!an||!Number.isInteger(season)||seen.has(id))continue;
  seen.add(id);
  out.push({eventId:id,startsAt:new Date(start).toISOString(),season,home:hn,away:an,homeId,awayId,neutral:c?.neutralSite===true});
 }
 return out.sort((a,b)=>Date.parse(a.startsAt)-Date.parse(b.startsAt));
}
/** Inclusive [from,to] day ranges no longer than `days`, as ESPN YYYYMMDD-YYYYMMDD strings. */
export function dayRanges(from:Date,to:Date,days:number):string[]{
 const out:string[]=[],DAYMS=86400000;
 for(let t=Date.UTC(from.getUTCFullYear(),from.getUTCMonth(),from.getUTCDate());t<=to.getTime();t+=days*DAYMS)
  {const a=ymd(new Date(t)),b=ymd(new Date(Math.min(to.getTime(),t+(days-1)*DAYMS)));out.push(a===b?a:a+"-"+b);}
 return out;
}
async function scoreboardEvents(sport:Sport,from:Date,to:Date,opts:{revalidate?:number;maxRequests?:number}={}):Promise<Event[]>{
 const ranges=dayRanges(from,to,SPORT_CONFIG[sport].chunkDays),limit=SPORT_CONFIG[sport].pageLimit;
 if(opts.maxRequests&&ranges.length>opts.maxRequests)throw new Error("Schedule range too long for this feed");
 const lists=await mapLimit(ranges,8,async range=>{
  const res=await fetch(espnScoreboardUrl(sport,range),opts.revalidate
   ?{signal:AbortSignal.timeout(10000),next:{revalidate:opts.revalidate}}:{signal:AbortSignal.timeout(10000),cache:"no-store"});
  if(!res.ok)throw new Error("Schedule provider HTTP "+res.status);
  const data=await res.json() as {events?:Event[]};
  if(!Array.isArray(data.events)||data.events.length>=limit)throw new Error("Schedule provider returned an invalid or truncated event list");
  return data.events;
 });
 return lists.flat();
}
export async function fetchUpcoming(sport:Sport,from:Date,to:Date,opts:{revalidate?:number;maxRequests?:number}={}):Promise<UpcomingGame[]>{
 // ESPN dates are US calendar days; widen by a day each side and filter by timestamp.
 const a=new Date(from.getTime()-86400000),b=new Date(to.getTime()+86400000);
 return parseUpcoming(await scoreboardEvents(sport,a,b,opts),from,to);
}

export type FinalScore={eventId:string;homeId:string;awayId:string;homeScore:number;awayScore:number};
/** Completed games with integer scores, keyed by provider event ID (for grading). */
export function parseFinals(events:Event[]):Map<string,FinalScore>{
 const out=new Map<string,FinalScore>();
 for(const e of events){
  if(!e?.status?.type?.completed||e.status.type.state!=="post")continue;
  const c=e.competitions?.[0];
  const home=c?.competitors?.find(x=>x.homeAway==="home") as (Competitor&{score?:string})|undefined;
  const away=c?.competitors?.find(x=>x.homeAway==="away") as (Competitor&{score?:string})|undefined;
  const hs=Number(home?.score),as=Number(away?.score),id=String(e.id||"").trim();
  if(!id||!home?.team?.id||!away?.team?.id||!Number.isInteger(hs)||!Number.isInteger(as)||hs<0||as<0)continue;
  out.set(id,{eventId:id,homeId:String(home.team.id),awayId:String(away.team.id),homeScore:hs,awayScore:as});
 }
 return out;
}
export async function fetchFinals(sport:Sport,from:Date,to:Date):Promise<Map<string,FinalScore>>{
 return parseFinals(await scoreboardEvents(sport,from,to));
}

/** Live scoreboard state per event: pre-game, in progress (with clock) or final. */
export type LiveGame={eventId:string;state:"pre"|"in"|"post";detail:string;homeId:string;awayId:string;homeScore:number|null;awayScore:number|null};
export function parseLive(events:Event[]):LiveGame[]{
 const out:LiveGame[]=[];
 for(const e of events){
  const st=e?.status?.type?.state,id=String(e?.id||"").trim();
  if(!id||(st!=="pre"&&st!=="in"&&st!=="post"))continue;
  const c=e.competitions?.[0];
  const home=c?.competitors?.find(x=>x.homeAway==="home") as (Competitor&{score?:string})|undefined;
  const away=c?.competitors?.find(x=>x.homeAway==="away") as (Competitor&{score?:string})|undefined;
  if(!home?.team?.id||!away?.team?.id)continue;
  const num=(v?:string)=>{const n=Number(v);return st!=="pre"&&v!==undefined&&v!==""&&Number.isFinite(n)?n:null;};
  out.push({eventId:id,state:st,detail:String(e.status?.type?.shortDetail||e.status?.type?.detail||"").slice(0,40),
   homeId:String(home.team.id),awayId:String(away.team.id),homeScore:num(home.score),awayScore:num(away.score)});
 }
 return out;
}
/** Yesterday through tomorrow (US days), uncached; the API route is cached ~20s at the CDN. */
export async function fetchLive(sport:Sport,now=new Date()):Promise<LiveGame[]>{
 const DAYMS=86400000;
 return parseLive(await scoreboardEvents(sport,new Date(now.getTime()-DAYMS),new Date(now.getTime()+DAYMS)));
}
