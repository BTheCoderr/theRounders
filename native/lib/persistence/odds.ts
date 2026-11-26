import {rest,readTeamRegistry} from "./history";
import {fetchUpcoming} from "../results/espnSchedule";
import {ODDS_MARKETS,ODDS_REGIONS,matchEspn,oddsSportKey,parseConsensus,shouldPoll,type OddsEvent} from "../providers/oddsApi";
import {decideSpend,oddsCost,spendPolicy,type Provider,type SpendState} from "../providers/spend";
import type {Sport} from "../sports";
import type {MarketQuote} from "../contracts";
import type {EspnLine} from "../results/espnLines";

const API="https://api.the-odds-api.com/v4";
const DAY=86400000;

/** Today's and this month's recorded usage for a provider (UTC). */
export async function spendState(provider:Provider,now=new Date()):Promise<SpendState>{
 const month=now.toISOString().slice(0,7)+"-01";
 const r=await rest(`rounders_provider_usage?select=day,credits,last_remaining&provider=eq.${provider}&day=gte.${month}&order=day.desc`);
 const rows=await r.json() as Array<{day:string;credits:number;last_remaining:number|null}>;
 const today=now.toISOString().slice(0,10);
 return {monthUsed:rows.reduce((s,x)=>s+(x.credits||0),0),dayUsed:rows.find(x=>x.day===today)?.credits??0,lastRemaining:rows[0]?.last_remaining??null};
}
export async function recordUsage(provider:Provider,credits:number,remaining:number|null,blocked=0){
 await rest("rpc/rounders_record_usage",{method:"POST",body:JSON.stringify({p_provider:provider,p_credits:credits,p_remaining:remaining,p_blocked:blocked})});
}
const header=(res:Response,name:string)=>{const v=Number(res.headers.get(name));return Number.isFinite(v)&&res.headers.get(name)!==null?v:null;};

/**
 * One odds capture for a sport, if the polling policy and the budget allow it.
 * Uses the free /events endpoint to decide, then one /odds request (3 credits).
 */
export async function captureOdds(sport:Sport,now=new Date()){
 const policy=spendPolicy("the-odds-api");
 if(!policy.enabled)return {sport,skipped:"disabled"};
 const key=process.env.ODDS_API_KEY!;
 const q=(extra:Record<string,string>)=>new URLSearchParams({apiKey:key,dateFormat:"iso",...extra}).toString();
 const ev=await fetch(`${API}/sports/${oddsSportKey(sport)}/events?${q({})}`,{cache:"no-store",signal:AbortSignal.timeout(10000)});
 if(!ev.ok)throw new Error("Odds events HTTP "+ev.status);
 const events=await ev.json() as Array<{commence_time:string}>;
 const last=await (await rest(`rounders_odds_snapshots?select=captured_at&sport=eq.${sport}&order=captured_at.desc&limit=1`)).json() as Array<{captured_at:string}>;
 const decision=shouldPoll(events.map(e=>e.commence_time),last[0]?.captured_at??null,now);
 if(!decision.poll)return {sport,skipped:decision.reason};
 const cost=oddsCost(ODDS_MARKETS.length,ODDS_REGIONS.length);
 const budget=decideSpend(policy,await spendState("the-odds-api",now),cost);
 if(!budget.allow){await recordUsage("the-odds-api",0,null,1);return {sport,skipped:budget.reason};}
 const res=await fetch(`${API}/sports/${oddsSportKey(sport)}/odds?${q({regions:ODDS_REGIONS.join(","),markets:ODDS_MARKETS.join(","),oddsFormat:"american"})}`,{cache:"no-store",signal:AbortSignal.timeout(15000)});
 await recordUsage("the-odds-api",header(res,"x-requests-last")??cost,header(res,"x-requests-remaining"));
 if(!res.ok)throw new Error("Odds HTTP "+res.status);
 const consensus=parseConsensus(await res.json() as OddsEvent[],sport);
 if(!consensus.length)return {sport,captured:0,reason:decision.reason};
 // Link to ESPN events (our prediction keys) by teams and start time.
 const [espn,registry]=await Promise.all([
  fetchUpcoming(sport,new Date(now.getTime()-6*3600000),new Date(now.getTime()+8*DAY),{revalidate:3600}).catch(()=>[]),
  readTeamRegistry(sport).catch(()=>new Map<string,string>())]);
 const games=espn.map(g=>({...g,home:registry.get(g.homeId)||g.home,away:registry.get(g.awayId)||g.away}));
 const captured_at=now.toISOString();
 const rows=consensus.filter(c=>Date.parse(c.startsAt)>now.getTime()).map(c=>({
  sport,provider:"the-odds-api",odds_event_id:c.oddsEventId,espn_event_id:matchEspn(c,games)?.eventId??null,
  starts_at:c.startsAt,home:c.home,away:c.away,captured_at,books:c.books,
  spread_home:c.spreadHome,total:c.total,home_win_prob:c.homeWinProb,quotes:c.quotes}));
 for(let i=0;i<rows.length;i+=100)
  await rest("rounders_odds_snapshots?on_conflict=provider,odds_event_id,captured_at",{method:"POST",headers:{Prefer:"resolution=ignore-duplicates,return=minimal"},body:JSON.stringify(rows.slice(i,i+100))});
 return {sport,captured:rows.length,linked:rows.filter(r=>r.espn_event_id).length,reason:decision.reason};
}

type SnapRow={provider?:string;odds_event_id:string;espn_event_id:string|null;starts_at:string;captured_at:string;books:number;spread_home:number|null;total:number|null;home_win_prob:number|null;quotes?:MarketQuote[]};
/** Licensed consensus first; ESPN's single-book line (internal only) when that is all we have. */
export const PROVIDER_RANK:Record<string,number>={"the-odds-api":0,"espn":1};
/** Latest pre-start consensus per ESPN event (for locking a market line next to a pick). */
export async function latestLines(sport:Sport,espnIds:string[]):Promise<Map<string,SnapRow>>{
 const ids=espnIds.filter(x=>/^\d+$/.test(x));const out=new Map<string,SnapRow>();
 for(let i=0;i<ids.length;i+=100){
  const r=await rest(`rounders_odds_snapshots?select=provider,odds_event_id,espn_event_id,starts_at,captured_at,books,spread_home,total,home_win_prob&sport=eq.${sport}&espn_event_id=in.(${ids.slice(i,i+100).join(",")})&order=captured_at.desc&limit=2000`);
  for(const s of await r.json() as SnapRow[]){
   if(!s.espn_event_id||Date.parse(s.captured_at)>=Date.parse(s.starts_at))continue;
   const have=out.get(s.espn_event_id);
   if(!have||(PROVIDER_RANK[s.provider||""]??9)<(PROVIDER_RANK[have.provider||""]??9))out.set(s.espn_event_id,s);
  }
 }
 return out;
}
/** Line shop: per-book quotes from the latest capture of each upcoming game. No provider call. */
export async function storedQuotes(sport:Sport,now=new Date()):Promise<{quotes:MarketQuote[];capturedAt:string|null}>{
 const r=await rest(`rounders_odds_snapshots?select=odds_event_id,captured_at,quotes,starts_at&sport=eq.${sport}&provider=eq.the-odds-api&starts_at=gt.${encodeURIComponent(now.toISOString())}&captured_at=gt.${encodeURIComponent(new Date(now.getTime()-DAY).toISOString())}&order=captured_at.desc&limit=500`);
 const rows=await r.json() as SnapRow[];const seen=new Set<string>();const quotes:MarketQuote[]=[];let newest:string|null=null;
 for(const s of rows){if(seen.has(s.odds_event_id))continue;seen.add(s.odds_event_id);newest??=s.captured_at;quotes.push(...(s.quotes||[]));}
 return {quotes,capturedAt:newest};
}
export type OpenClose={espn_event_id:string|null;open_spread_home:number|null;close_spread_home:number|null;close_home_win_prob:number|null;opened_at:string;closed_at:string;captures:number};
export async function openCloseLines(sport:Sport,espnIds:string[],provider="the-odds-api"):Promise<Map<string,OpenClose>>{
 const ids=espnIds.filter(x=>/^\d+$/.test(x));const out=new Map<string,OpenClose>();
 for(let i=0;i<ids.length;i+=100){
  const r=await rest(`rounders_odds_open_close?select=espn_event_id,open_spread_home,close_spread_home,close_home_win_prob,opened_at,closed_at,captures&sport=eq.${sport}&provider=eq.${encodeURIComponent(provider)}&espn_event_id=in.(${ids.slice(i,i+100).join(",")})`);
  for(const x of await r.json() as OpenClose[])if(x.espn_event_id)out.set(x.espn_event_id,x);
  // ESPN carries the book's own opening line: prefer it to our first capture (which may be hours later).
  if(provider==="espn"){
   const f=await rest(`rounders_odds_snapshots?select=espn_event_id,captured_at,open:quotes->0->open&provider=eq.espn&sport=eq.${sport}&espn_event_id=in.(${ids.slice(i,i+100).join(",")})&order=captured_at.asc&limit=2000`);
   const seen=new Set<string>();
   for(const x of await f.json() as Array<{espn_event_id:string;open?:{spreadHome?:number|null}|null}>){
    if(seen.has(x.espn_event_id))continue;seen.add(x.espn_event_id);
    const o=x.open?.spreadHome,cur=out.get(x.espn_event_id);
    if(cur&&typeof o==="number"&&Number.isFinite(o))out.set(x.espn_event_id,{...cur,open_spread_home:o});
   }
  }
 }
 return out;
}

/**
 * Store ESPN's pregame lines as provider "espn" snapshots (one book, internal use only).
 * Called from the hourly prediction job, so the last capture before start is within an hour
 * of tip-off. The raw odds object is kept for auditing the parser; it is never served publicly.
 */
export async function saveEspnLines(sport:Sport,lines:readonly EspnLine[],now=new Date()){
 const captured_at=now.toISOString();
 const rows=lines.filter(l=>Date.parse(l.startsAt)>now.getTime()).map(l=>({
  sport,provider:"espn",odds_event_id:l.eventId,espn_event_id:l.eventId,starts_at:l.startsAt,home:l.home,away:l.away,
  captured_at,books:1,spread_home:l.spreadHome,total:l.total,home_win_prob:l.homeWinProb,
  quotes:[{book:l.book,homeMoneyline:l.homeMoneyline,awayMoneyline:l.awayMoneyline,open:l.open,raw:l.raw}]}));
 for(let i=0;i<rows.length;i+=200)
  await rest("rounders_odds_snapshots?on_conflict=provider,odds_event_id,captured_at",{method:"POST",headers:{Prefer:"resolution=ignore-duplicates,return=minimal"},body:JSON.stringify(rows.slice(i,i+200))});
 return rows.length;
}
