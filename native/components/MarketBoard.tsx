"use client";
import {useEffect,useMemo,useState} from "react";
import type {MarketName,MarketQuote} from "../lib/contracts";
import {pct,signed,type PredictionView,type ProductSport} from "../lib/clientTypes";
import {teamKey} from "../lib/engine/market";
import {authHeaders} from "../lib/clientAuth";
import AddPaperBet from "./AddPaperBet";

const markets:[MarketName,string][]=[["moneyline","Moneyline"],["spread","Spread"],["total","Total"]];
const fmt=(n:number)=>n>0?"+"+n:String(n);
const implied=(odds:number)=>odds<0?(-odds)/((-odds)+100)*100:100/(odds+100)*100;
type Feed={mode:string;fresh:boolean;provider:string;fallback:boolean;ageMs:number};

export default function MarketBoard({sport}:{sport:ProductSport}){
 const [market,setMarket]=useState<MarketName>("moneyline"),[quotes,setQuotes]=useState<MarketQuote[]>([]),[loading,setLoading]=useState(true);
 const [open,setOpen]=useState<string|null>(null),[stake,setStake]=useState(25),[refresh,setRefresh]=useState(0),[feedError,setFeedError]=useState(false);
 const [feed,setFeed]=useState<Feed>({mode:"unavailable",fresh:false,provider:"",fallback:true,ageMs:0});
 const [picks,setPicks]=useState<PredictionView[]>([]);
 useEffect(()=>{
  const c=new AbortController();setLoading(true);setFeedError(false);setOpen(null);setQuotes([]);setPicks([]);
  fetch("/api/markets?sport="+sport,{signal:c.signal,cache:"no-store"})
   .then(async r=>{if(!r.ok)throw new Error("Feed unavailable");return r.json()})
   .then(d=>{if(c.signal.aborted)return;setQuotes(d.mode==="live"&&Array.isArray(d.markets)?d.markets.filter((q:MarketQuote)=>q.state==="live"&&q.sport===sport&&Date.parse(q.startTime)>Date.now()):[]);
    setFeed({mode:d.mode||"unavailable",fresh:d.mode==="live"&&d.fresh===true,provider:d.provider||"",fallback:d.fallback!==false,ageMs:Number.isFinite(d.ageMs)?d.ageMs:0})})
   .catch(()=>{if(!c.signal.aborted)setFeedError(true)})
   .finally(()=>{if(!c.signal.aborted)setLoading(false)});
  fetch("/api/predictions?sport="+sport,{signal:c.signal,headers:authHeaders()})
   .then(r=>r.ok?r.json():null).then(d=>{if(!c.signal.aborted)setPicks(Array.isArray(d?.predictions)?d.predictions:[])}).catch(()=>{});
  return()=>c.abort();
 },[sport,refresh]);
 const live=!feedError&&feed.mode==="live"&&!feed.fallback;
 const selections=useMemo(()=>{const map=new Map<string,MarketQuote[]>();quotes.filter(q=>q.market===market).forEach(q=>{const key=JSON.stringify([q.eventId,q.market,q.selection,q.line??null,q.state]);map.set(key,[...(map.get(key)||[]),q])});return [...map.entries()]},[quotes,market]);
 // Model numbers come only from stored engine predictions for the same real game.
 const pickFor=(q:MarketQuote)=>picks.find(p=>teamKey(p.home)===teamKey(q.home)&&teamKey(p.away)===teamKey(q.away)&&Math.abs(Date.parse(p.startsAt)-Date.parse(q.startTime))<=3600000&&p.status==="pending");
 return <section className="block market" id="markets"><div className="blockHead"><h2>Line shop</h2><span className={"chip "+(live?"liveChip":"warnChip")}>{live?"LIVE ODDS":"ODDS UNAVAILABLE"}</span></div>
  <div className="feedStatus"><span className={"feedDot "+(feed.fresh?"ok":"stale")}/><span>{live?(feed.fresh?"Live prices":"Live prices are stale"):"Verified sportsbook prices are not available"}{feed.ageMs&&live?" · "+Math.round(feed.ageMs/1000)+"s ago":""}</span><button className="refreshFeed" onClick={()=>setRefresh(v=>v+1)}>Refresh</button></div>
  <div className="marketTabs">{markets.map(([id,label])=><button className={market===id?"active":""} onClick={()=>setMarket(id)} key={id}>{label}</button>)}</div>
  {loading?<p className="muted">Loading market feed…</p>:feedError?<p className="muted" role="status">Unable to load markets. Try Refresh.</p>:selections.length===0?<p className="muted">No matching markets available.</p>:
  <div className="gameList">{selections.map(([key,group])=>{
   const first=group[0],best=group.reduce((a,b)=>b.price>a.price?b:a),isOpen=open===key,prob=implied(best.price);
   const pick=live?pickFor(first):undefined;
   const modelProb=pick&&market==="moneyline"?(best.selection===pick.home?pick.homeWinProbability*100:best.selection===pick.away?(1-pick.homeWinProbability)*100:null):null;
   return <div className={"gameWrap "+(isOpen?"opened":"")} key={key}><button className="gameCard" onClick={()=>setOpen(isOpen?null:key)}>
    <div className="gameInfo"><span className="gameTime">{new Date(first.startTime).toLocaleString([],{weekday:"short",hour:"numeric",minute:"2-digit"})}</span><div className="teams"><strong>{first.away}</strong><span>@</span><strong>{first.home}</strong></div><div className="signal"><span>{first.selection}{first.line!==undefined?" "+(market==="total"?String(first.line):fmt(first.line)):""}</span></div></div>
    <div className="books">{group.map((q,i)=><div className={q===best?"quote best":"quote"} key={q.book+":"+i}><small>{q.book}</small>{q.line!==undefined&&<span className="line">{market==="total"?String(q.line):fmt(q.line)}</span>}<b>{fmt(q.price)}</b>{q===best&&<em>BEST</em>}</div>)}</div>
    <div className="fresh"><span className={"state "+first.state}>{first.state}</span><small>{isOpen?"Close":"Details"} ›</small></div></button>
    {isOpen&&<div className="analytics">
     <div className="metric"><small>Best price</small><strong>{best.book}</strong><span>{fmt(best.price)} · {prob.toFixed(1)}% implied</span></div>
     {pick?<>
      <div className="metric"><small>Rounders projection</small><strong>{pick.projectedWinner}</strong><span>{pct(pick.projectedWinner===pick.home?pick.homeWinProbability:1-pick.homeWinProbability)} · {pick.modelVersion}</span></div>
      <div className="metric"><small>Model spread / total</small><strong>{pick.projectedSpreadHome===null?"Pro":signed(pick.projectedSpreadHome)} / {pick.projectedTotal===null?"Pro":pick.projectedTotal.toFixed(1)}</strong><span>{pick.home} perspective</span></div>
      {modelProb!==null?<div className="metric edge"><small>Model vs market</small><strong>{signed(modelProb-prob)} pts</strong><span>probability difference, live prices only</span></div>:null}
     </>:<div className="metric"><small>Rounders projection</small><strong>{live?"No stored prediction":"Hidden on demo prices"}</strong><span>{live?"Predictions are stored for each day's games":"Model comparisons use live odds only"}</span></div>}
     <div className="paperTicket"><div><small>PAPER TICKET</small><strong>{best.selection} {best.line!==undefined?fmt(best.line):""} {fmt(best.price)}</strong></div><label>$<input type="number" min="1" max="100000" value={stake} onChange={e=>setStake(Number(e.target.value))}/></label><AddPaperBet eventId={first.eventId} sport={first.sport} matchup={first.away+" @ "+first.home} market={market} selection={best.selection} line={best.line} price={best.price} book={best.book} stake={stake} dataState={best.state}/></div>
    </div>}
   </div>})}</div>}
  <p className="feedNote">Prices are compared only when the game, market, side and line match. Price gaps are not steam or reverse line movement. Paper tickets never place real wagers.</p>
 </section>;
}
