"use client";
import {useEffect,useState} from "react";
import {num,pct,type PerformanceResponse,type ProductSport,type Summary} from "../lib/clientTypes";

function Tiles({s}:{s:Summary}){
 const tiles:[string,string,string][]=[
  ["Graded games",String(s.games),`${s.decided} decided`],
  ["Winner accuracy",pct(s.winnerAccuracy),"straight up"],
  ["Brier score",num(s.brierScore,3),"lower is better; 0.25 = coin flip"],
  ["Log loss",num(s.logLoss,3),"lower is better"],
  ["Spread error",num(s.marginMAE,1),"mean absolute points"],
  ["Total error",num(s.totalMAE,1),`mean absolute points (${s.totalGames})`]
 ];
 return <div className="tileGrid">{tiles.map(([a,b,c])=><div className="metric" key={a}><small>{a}</small><strong>{b}</strong><span>{c}</span></div>)}</div>;
}
function Calibration({s}:{s:Summary}){
 const rows=s.calibration.filter(b=>b.forecasts>0);
 if(!rows.length)return null;
 return <table className="dataTable"><caption>Calibration: favorites by stated win probability</caption>
  <thead><tr><th>Stated</th><th>Games</th><th>Average stated</th><th>Actually won</th></tr></thead>
  <tbody>{rows.map(b=><tr key={b.from}><td>{Math.round(b.from*100)}–{Math.min(100,Math.round(b.to*100))}%</td><td>{b.forecasts}</td><td>{pct(b.meanForecast)}</td><td>{pct(b.observedRate)}</td></tr>)}</tbody></table>;
}
function Records({s}:{s:Summary}){
 if(!s.againstSpread.games&&!s.againstTotal.games)return <p className="muted small">Against-the-spread and over/under records appear once live pregame market lines are captured with predictions.</p>;
 const rec=(r:Summary["againstSpread"])=>`${r.wins}-${r.losses}-${r.pushes} (${pct(r.winRate)})`;
 return <p className="muted small">Versus live pregame lines: spread {rec(s.againstSpread)} · total {rec(s.againstTotal)}. Small samples are noisy; this is not evidence of profit.</p>;
}
export default function Performance({sport}:{sport:ProductSport}){
 const [d,setD]=useState<PerformanceResponse|null>(null),[error,setError]=useState("");
 useEffect(()=>{
  const c=new AbortController();setD(null);setError("");
  fetch("/api/performance?sport="+sport,{signal:c.signal,cache:"no-store"})
   .then(async r=>{const x=await r.json() as PerformanceResponse;if(!c.signal.aborted)setD(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Performance data is unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const champ=d?.live?.find(x=>x.champion);
 return <section className="panel stack" id="performance">
  <div className="sectionHead"><div><p className="tag">TRACK RECORD · FREE FOR EVERYONE</p><h2>How the {sport} model has actually done.</h2>
   <p className="muted">Live results count only predictions stored before the game and graded after it. Backtests are simulated on past seasons and shown separately.</p></div></div>
  {error?<p className="muted">{error}</p>:!d?<p className="muted" role="status">Loading track record…</p>:!d.ready?<p className="muted">{d.reason}</p>:<>
   <h3>Live record · {d.championLabel}</h3>
   {champ&&champ.summary.games>0?<><Tiles s={champ.summary}/><Calibration s={champ.summary}/><Records s={champ.summary}/>
    <p className="muted small">{champ.from?.slice(0,10)} to {champ.through?.slice(0,10)}</p></>
    :<p className="muted">No graded live predictions yet. The record starts with the first stored {sport} slate and grows after every game.</p>}
   {d.live&&d.live.some(x=>!x.champion&&x.summary.games>0)?<table className="dataTable"><caption>Every candidate model, scored on the same live games</caption>
    <thead><tr><th>Model</th><th>Games</th><th>Accuracy</th><th>Brier</th><th>Spread error</th><th>Total error</th></tr></thead>
    <tbody>{d.live.map(m=><tr key={m.model} className={m.champion?"champ":""}><td>{m.label}{m.champion?" (live)":""}</td><td>{m.summary.games}</td><td>{pct(m.summary.winnerAccuracy)}</td><td>{num(m.summary.brierScore,3)}</td><td>{num(m.summary.marginMAE,1)}</td><td>{num(m.summary.totalMAE,1)}</td></tr>)}</tbody></table>:null}
   <h3>Walk-forward backtest</h3>
   {d.backtest?<>
    <p className="muted small">{d.backtest.evaluatedGames} games over {d.backtest.evaluatedWeeks} weeks, seasons {d.backtest.seasons.join(", ")||"—"} · run {d.backtest.runDay} · {d.backtest.dataSource}. Each week every model is refit on earlier games only.</p>
    <table className="dataTable"><thead><tr><th>Model</th><th>Accuracy</th><th>Brier</th><th>Log loss</th><th>Spread error</th></tr></thead>
     <tbody>{d.backtest.models.map(m=><tr key={m.model} className={m.model===d.champion?"champ":""}><td>{m.label}{m.model===d.champion?" (live)":""}</td><td>{pct(m.summary.winnerAccuracy)}</td><td>{num(m.summary.brierScore,3)}</td><td>{num(m.summary.logLoss,3)}</td><td>{num(m.summary.marginMAE,2)}</td></tr>)}</tbody></table>
    <p className="muted small">Totals: {d.backtest.totals.model} error {num(d.backtest.totals.summary.mae,1)} vs league-average baseline {num(d.backtest.totals.baseline.mae,1)}.</p>
    {d.backtest.promotion.map(p=><p className="muted small" key={p.challenger}>{p.recommend?"✓":"·"} {p.challenger} vs {p.champion}: {p.reasons[0]}</p>)}
   </>:<p className="muted">No backtest stored yet. It runs daily once the verified archive is populated.</p>}
   {d.notes?.map(n=><p className="feedNote" key={n}>{n}</p>)}
  </>}
 </section>;
}
