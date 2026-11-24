"use client";
import {useEffect,useState} from "react";
import type {MarketQuote} from "../lib/contracts";
import {findLineShopGaps,type LineShopGap} from "../lib/signals";
import type {ProductSport} from "../lib/clientTypes";
const fmt=(n:number)=>n>0?"+"+n:String(n);
export default function SharpSignals({sport}:{sport:ProductSport}){
 const [gaps,setGaps]=useState<LineShopGap[]>([]),[loading,setLoading]=useState(true),[error,setError]=useState(false);
 useEffect(()=>{
  const ctrl=new AbortController();setLoading(true);setError(false);
  setGaps([]);
  void fetch("/api/markets?sport="+sport,{signal:ctrl.signal,cache:"no-store"})
   .then(async response=>{
    if(!response.ok)throw new Error("Feed unavailable");
    const body=await response.json() as {mode?:string;fallback?:boolean;markets?:MarketQuote[]};
    if(body.mode!=="live"||body.fallback!==false)throw new Error("Feed unavailable");
    if(!ctrl.signal.aborted)setGaps(findLineShopGaps((Array.isArray(body.markets)?body.markets:[]).filter(q=>q.sport===sport&&q.state==="live"&&Date.parse(q.startTime)>Date.now())).slice(0,8));
   }).catch(()=>{if(!ctrl.signal.aborted)setError(true)})
   .finally(()=>{if(!ctrl.signal.aborted)setLoading(false)});
  return()=>ctrl.abort();
 },[sport]);
 return <section className="signalsPanel" id="signals"><div className="sectionHead"><div>
  <p className="tag">LINE SHOP SIGNALS</p><h2>Compare prices, not invented movement.</h2>
  <p className="muted">Same selection and line across different books. Price differences are not steam moves or reverse line movement; those need verified historical odds.</p>
 </div><span className="modelBadge">MARKET COMPARISON</span></div>
 {loading?<p className="muted" role="status">Comparing current market snapshots…</p>:error?<p className="muted" role="status">Market feeds unavailable. No signal claimed.</p>:gaps.length===0?<p className="muted">No comparable multi-book price gaps found. Historical movement alerts are not enabled.</p>:null}
 <div className="signalList">{gaps.map(g=><div className="signalRow" style={{display:"grid",gridTemplateColumns:"repeat(2,minmax(0,1fr))",gap:12}} key={g.key}>
  <div style={{gridColumn:"1 / -1",overflowWrap:"anywhere"}}><span className="signalKind">{g.market.toUpperCase()} · {g.state.toUpperCase()}</span><strong>{g.matchup}</strong><small>{g.sport} · {g.selection}{g.line===undefined?"":" "+g.line}</small></div>
  <div className="signalMetric"><small>BEST PRICE</small><b>{fmt(g.bestPrice)}</b><small>{g.bestBook}</small></div>
  <div className="signalMetric"><small>IMPLIED PROBABILITY GAP</small><b>{g.impliedGapPoints.toFixed(2)} pts</b><small>vs {g.worstBook} ({fmt(g.worstPrice)})</small></div>
 </div>)}</div>
 </section>
}
