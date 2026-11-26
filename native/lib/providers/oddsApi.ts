import {SPORT_CONFIG,type Sport} from "../sports.ts";
import {teamKey} from "../engine/market.ts";
import type {MarketQuote,MarketName} from "../contracts";

/**
 * The Odds API v4 (paid plan required for production volumes; commercial display allowed,
 * raw resale prohibited). One request per sport covers h2h, spreads and totals for US books:
 * cost = 3 markets x 1 region = 3 credits. Empty responses cost nothing.
 */
export const ODDS_MARKETS=["h2h","spreads","totals"] as const;
export const ODDS_REGIONS=["us"] as const;
export const oddsSportKey=(s:Sport)=>SPORT_CONFIG[s].odds;

type Outcome={name:string;price:number;point?:number};
type Book={key:string;title:string;last_update?:string;markets?:Array<{key:string;last_update?:string;outcomes?:Outcome[]}>};
export type OddsEvent={id:string;sport_key:string;commence_time:string;home_team:string;away_team:string;bookmakers?:Book[]};

export type Consensus={oddsEventId:string;startsAt:string;home:string;away:string;books:number;
 spreadHome:number|null;total:number|null;homeWinProb:number|null;quotes:MarketQuote[]};

const median=(xs:number[])=>{if(!xs.length)return null;const s=[...xs].sort((a,b)=>a-b),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;};
/** American odds to implied probability (with vig). */
export const implied=(price:number)=>price>0?100/(price+100):-price/(-price+100);
const NAMES:Record<string,MarketName>={h2h:"moneyline",spreads:"spread",totals:"total"};

/**
 * Consensus per game: median home spread, median total, and the vig-free home win
 * probability (each book's two-way moneyline normalized to 100%, then averaged).
 * Books missing a market simply don't contribute to it; nothing is imputed.
 */
export function parseConsensus(events:OddsEvent[],sport:Sport):Consensus[]{
 const out:Consensus[]=[];
 for(const e of events){
  if(!e?.id||!e.home_team||!e.away_team||!Number.isFinite(Date.parse(e.commence_time)))continue;
  const h=teamKey(e.home_team),a=teamKey(e.away_team);
  const spreads:number[]=[],totals:number[]=[],probs:number[]=[],quotes:MarketQuote[]=[];
  let books=0;
  for(const b of e.bookmakers||[]){
   let used=false;
   for(const m of b.markets||[]){
    const name=NAMES[m.key];if(!name)continue;
    const oc=(m.outcomes||[]).filter(o=>Number.isFinite(o.price)&&o.price!==0);
    for(const o of oc)quotes.push({eventId:e.id,sport,market:name,selection:o.name,line:o.point,price:o.price,book:b.title,
     updatedAt:m.last_update||b.last_update||"",state:"live",away:e.away_team,home:e.home_team,startTime:e.commence_time});
    if(m.key==="spreads"){const p=oc.find(o=>teamKey(o.name)===h);if(p&&Number.isFinite(p.point)){spreads.push(p.point!);used=true;}}
    if(m.key==="totals"){const p=oc.find(o=>/^over$/i.test(o.name));if(p&&Number.isFinite(p.point)){totals.push(p.point!);used=true;}}
    if(m.key==="h2h"){
     const ph=oc.find(o=>teamKey(o.name)===h),pa=oc.find(o=>teamKey(o.name)===a);
     if(ph&&pa){const ih=implied(ph.price),ia=implied(pa.price);if(ih+ia>0){probs.push(ih/(ih+ia));used=true;}}
    }
   }
   if(used)books++;
  }
  if(!books)continue;
  const hp=probs.length?probs.reduce((s,x)=>s+x,0)/probs.length:null;
  out.push({oddsEventId:e.id,startsAt:new Date(e.commence_time).toISOString(),home:e.home_team,away:e.away_team,books,
   spreadHome:median(spreads),total:median(totals),homeWinProb:hp===null?null:Number(Math.min(0.999,Math.max(0.001,hp)).toFixed(4)),quotes});
 }
 return out;
}
/** Match an odds event to an ESPN event: same home/away teams, start within 6 hours. */
export function matchEspn<T extends {eventId:string;startsAt:string;home:string;away:string}>(c:{home:string;away:string;startsAt:string},espn:readonly T[]):T|null{
 const h=teamKey(c.home),a=teamKey(c.away),t=Date.parse(c.startsAt);
 let best:T|null=null,gap=Infinity;
 for(const g of espn){
  if(teamKey(g.home)!==h||teamKey(g.away)!==a)continue;
  const d=Math.abs(Date.parse(g.startsAt)-t);
  if(d<=6*3600000&&d<gap){best=g;gap=d;}
 }
 return best;
}
/**
 * Polling policy (keeps credits predictable):
 *  - closing: a game starts within 45 minutes and the last capture is 15+ minutes old;
 *  - opening/updates: games in the next 7 days and the last capture is 6+ hours old.
 */
export function shouldPoll(starts:readonly string[],lastCaptureAt:string|null,now:Date):{poll:boolean;reason:string}{
 const t=now.getTime(),last=lastCaptureAt?Date.parse(lastCaptureAt):0;
 const upcoming=starts.map(s=>Date.parse(s)).filter(s=>s>t&&s<t+7*86400000);
 if(!upcoming.length)return {poll:false,reason:"no games in the next 7 days"};
 if(upcoming.some(s=>s-t<=45*60000)&&t-last>=15*60000)return {poll:true,reason:"closing window"};
 if(t-last>=6*3600000)return {poll:true,reason:"opening/update"};
 return {poll:false,reason:"recently captured"};
}
