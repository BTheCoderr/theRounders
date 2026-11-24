"use client";
import {useEffect,useState} from "react";
import {kickoff,pct,signed,type PredictionView,type PredictionsResponse,type ProductSport} from "../lib/clientTypes";
import {authHeaders} from "../lib/clientAuth";

type Insight={mode:"ai"|"model-summary";answer:string;notice:string};
function Explain({sport,p}:{sport:ProductSport;p:PredictionView}){
 const [open,setOpen]=useState(false),[q,setQ]=useState("Why does the model lean this way, and what could it be missing?");
 const [busy,setBusy]=useState(false),[result,setResult]=useState<Insight|null>(null),[error,setError]=useState("");
 async function ask(){
  setBusy(true);setError("");setResult(null);
  try{
   const r=await fetch("/api/ai/matchup",{method:"POST",headers:{"Content-Type":"application/json",...authHeaders()},
    body:JSON.stringify({sport,away:p.away,home:p.home,question:q,eventId:p.eventId})});
   const d=await r.json();
   if(!r.ok)throw new Error(d.error||"Analysis unavailable");
   setResult(d as Insight);
  }catch(e){setError(e instanceof Error?e.message:"Analysis unavailable")}finally{setBusy(false)}
 }
 if(!open)return <button className="linkButton" onClick={()=>setOpen(true)}>Explain this pick ›</button>;
 return <div className="explain">
  <label htmlFor={"q-"+p.eventId}>Ask about this matchup</label>
  <div className="explainRow"><input id={"q-"+p.eventId} value={q} maxLength={240} onChange={e=>setQ(e.target.value)}/><button disabled={busy||q.trim().length<3} onClick={ask}>{busy?"Thinking…":"Ask"}</button></div>
  {error&&<p className="warn" role="alert">{error}</p>}
  {result&&<div className="insight"><span className="modelBadge">{result.mode==="ai"?"AI EXPLANATION":"MODEL SUMMARY"}</span><p>{result.answer}</p><small>{result.notice}</small></div>}
 </div>;
}
function Card({sport,p}:{sport:ProductSport;p:PredictionView}){
 const favP=p.projectedWinner===p.home?p.homeWinProbability:1-p.homeWinProbability;
 const locked=new Set(p.locked||[]);
 return <article className="pickCard">
  <div className="pickHead"><span className="gameTime">{kickoff(p.startsAt)}</span>
   {p.status==="graded"&&p.final?<span className="state graded">FINAL {p.away} {p.final.away} · {p.home} {p.final.home}</span>:p.status==="void"?<span className="state">VOID</span>:<span className="state model">MODEL</span>}
  </div>
  <h3>{p.away} <span>@</span> {p.home}{p.neutral?<small> (neutral)</small>:null}</h3>
  <div className="pickMain"><div><small>Projected winner</small><strong>{p.projectedWinner}</strong><span>{pct(favP)} model win probability</span></div>
   <div className="probBar" aria-hidden="true"><i style={{width:(p.homeWinProbability*100).toFixed(1)+"%"}}/></div></div>
  <div className="pickStats">
   <div><small>Spread ({p.home})</small><strong>{p.projectedSpreadHome===null?(locked.has("spread")?"Pro":"—"):signed(p.projectedSpreadHome)}</strong></div>
   <div><small>Total</small><strong>{p.projectedTotal===null?(locked.has("total")?"Pro":"—"):p.projectedTotal.toFixed(1)}</strong></div>
   <div><small>Projected score</small><strong>{p.projectedAway===null||p.projectedHome===null?(locked.has("score")?"Pro":"—"):`${p.projectedAway.toFixed(0)}–${p.projectedHome.toFixed(0)}`}</strong></div>
   <div><small>Market (live)</small><strong>{p.market?`${p.market.spreadHome===null?"—":signed(p.market.spreadHome)} / ${p.market.total??"—"}`:locked.has("market")?"Edge":"Not captured"}</strong></div>
  </div>
  <p className="provenance">{p.modelVersion} · frozen {new Date(p.predictedAt).toLocaleString()} · trained on {p.trainingGames} completed games</p>
  {locked.size?<p className="lockNote">Spreads, totals and scores are part of <a href="/pricing">Rounders Pro</a>. Winners and probabilities stay free.</p>:null}
  {p.status==="pending"?<Explain sport={sport} p={p}/>:null}
 </article>;
}
export default function Predictions({sport}:{sport:ProductSport}){
 const [data,setData]=useState<PredictionsResponse|null>(null),[error,setError]=useState("");
 useEffect(()=>{
  const c=new AbortController();setData(null);setError("");
  fetch("/api/predictions?sport="+sport,{signal:c.signal,headers:authHeaders(),cache:"no-store"})
   .then(async r=>{const d=await r.json() as PredictionsResponse;if(!c.signal.aborted)setData(d)})
   .catch(()=>{if(!c.signal.aborted)setError("Predictions are unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const cadence=sport==="NBA"?"Today's NBA slate, frozen before tip-off each day.":"This week's NFL games, frozen on Tuesday (later additions within two days of kickoff).";
 return <section className="panel stack" id="predictions">
  <div className="sectionHead"><div><p className="tag">{sport} PREDICTIONS</p><h2>{sport==="NBA"?"Today's projections.":"This week's projections."}</h2>
   <p className="muted">{cadence} Every prediction is stored with its timestamp and never edited, then graded after the game.</p></div>
   {data?.modelLabel?<span className="modelBadge">{data.modelLabel}</span>:null}</div>
  {error?<p className="muted" role="status">{error}</p>:!data?<p className="muted" role="status">Loading predictions…</p>:
   !data.ready?<p className="muted">{data.reason||"Predictions are not available yet."}</p>:
   data.predictions.length===0?<p className="muted">No {sport} games in the current window. {sport==="NFL"?"The week's slate is stored on Tuesday.":"The day's slate is stored each morning (Eastern)."}</p>:
   <div className="pickGrid">{data.predictions.map(p=><Card key={p.eventId} sport={sport} p={p}/>)}</div>}
  {data?.notice?<p className="feedNote">{data.notice}</p>:null}
 </section>;
}
