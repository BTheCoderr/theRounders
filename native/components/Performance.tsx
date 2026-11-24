"use client";
import {useEffect,useState} from "react";
import {num,pct,type PerformanceResponse,type ProductSport,type Summary} from "../lib/clientTypes";

function Strip({s}:{s:Summary}){
 const tiles:[string,string,string][]=[
  ["Graded",String(s.games),"games"],
  ["Accuracy",pct(s.winnerAccuracy,0),"straight up"],
  ["Brier",num(s.brierScore,3),"0.250 = coin flip"],
  ["Spread error",num(s.marginMAE,1),"points"]
 ];
 return <div className="statStrip">{tiles.map(([a,b,c])=><div key={a}><small>{a}</small><strong>{b}</strong><span>{c}</span></div>)}</div>;
}
function Calibration({s}:{s:Summary}){
 const rows=s.calibration.filter(b=>b.forecasts>0);
 if(!rows.length)return null;
 return <div className="calib" aria-label="Calibration">
  {rows.map(b=><div key={b.from} className="calibRow">
   <span>{Math.round(b.from*100)}–{Math.min(100,Math.round(b.to*100))}%</span>
   <div className="calibTrack"><i className="said" style={{width:(b.meanForecast??0)*100+"%"}}/><i className="did" style={{width:(b.observedRate??0)*100+"%"}}/></div>
   <span>{pct(b.observedRate,0)} <small>({b.forecasts})</small></span>
  </div>)}
  <p className="fine">Thin bar: what the model said. Thick bar: how often those favorites actually won.</p>
 </div>;
}
export default function Performance({sport}:{sport:ProductSport}){
 const [d,setD]=useState<PerformanceResponse|null>(null),[error,setError]=useState("");
 useEffect(()=>{
  const c=new AbortController();setD(null);setError("");
  fetch("/api/performance?sport="+sport,{signal:c.signal,cache:"no-store"})
   .then(async r=>{const x=await r.json() as PerformanceResponse;if(!c.signal.aborted)setD(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Track record is unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const champ=d?.live?.find(x=>x.champion);
 const bt=d?.backtest;
 const btChamp=bt?.models.find(m=>m.model===d?.champion);
 return <section className="block" id="performance">
  <div className="blockHead"><h2>Track record</h2><span className="chip free">FREE</span></div>
  {error?<p className="empty">{error}</p>:!d?<div className="statStrip skeleton"/>:!d.ready?<p className="empty">{d.reason}</p>:<>
   {champ&&champ.summary.games>0?<><Strip s={champ.summary}/><Calibration s={champ.summary}/></>
    :<div className="emptyRecord"><b>Record starts with the first locked slate.</b><span>Every {sport} game is graded after the final and added here automatically.</span></div>}
   <a className="textButton" href={"/record?sport="+sport}>Every graded pick →</a>
   {bt&&btChamp?<details className="more"><summary>Backtest: {bt.evaluatedGames.toLocaleString()} past games · {pct(btChamp.summary.winnerAccuracy,1)} accuracy</summary>
    <p className="fine">Weekly walk-forward over seasons {bt.seasons.join(", ")}: each week every model is refit on earlier games only. Simulated on history, not published at the time.</p>
    <table className="dataTable"><thead><tr><th>Model</th><th>Acc.</th><th>Brier</th><th>Spread err.</th></tr></thead>
     <tbody>{bt.models.map(m=><tr key={m.model} className={m.model===d.champion?"champ":""}><td>{m.label}</td><td>{pct(m.summary.winnerAccuracy,1)}</td><td>{num(m.summary.brierScore,3)}</td><td>{num(m.summary.marginMAE,1)}</td></tr>)}</tbody></table>
   </details>:null}
  </>}
 </section>;
}
