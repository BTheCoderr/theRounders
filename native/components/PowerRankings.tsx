"use client";
import {useEffect,useState} from "react";
import type {ProductSport} from "../lib/clientTypes";

type Rank={rank:number;team:string;rating:number;games:number;record:{wins:number;losses:number;ties:number};averageOpponentRating:number;recentForm:number};
type Board={dataState:"external"|"simulated";provider:string;fallback:boolean;coverage:string;rankings:Rank[];notes:string[];retrievedAt:string};
export default function PowerRankings({sport}:{sport:ProductSport}){
 const [b,setB]=useState<Board|null>(null),[error,setError]=useState(""),[all,setAll]=useState(false);
 useEffect(()=>{
  const c=new AbortController();setB(null);setError("");setAll(false);
  fetch("/api/power-rankings?sport="+sport,{signal:c.signal})
   .then(async r=>{if(!r.ok)throw new Error();const x=await r.json() as Board;if(!c.signal.aborted)setB(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Rankings are unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const rows=b?(all?b.rankings:b.rankings.slice(0,10)):[];
 return <section className="panel stack" id="rankings">
  <div className="sectionHead"><div><p className="tag">POWER INDEX · {sport}</p><h2>Who is actually good.</h2>
   <p className="muted">Schedule-adjusted point margin per game, weighted toward recent results. A rating of +5 means about five points better than an average team on a neutral floor.</p></div>
   {b?<span className={"state "+(b.dataState==="simulated"?"simulated":"model")}>{b.dataState==="simulated"?"SIMULATED":"MODEL"}</span>:null}</div>
  {error?<p className="muted">{error}</p>:!b?<p className="muted" role="status">Loading rankings…</p>:<>
   <table className="dataTable"><thead><tr><th>#</th><th>Team</th><th>Rating</th><th>Opp. strength</th><th>Last 5</th></tr></thead>
    <tbody>{rows.map(r=><tr key={r.team}><td>{r.rank}</td><td>{r.team}</td><td>{r.rating>0?"+":""}{r.rating.toFixed(1)}</td><td>{r.averageOpponentRating>0?"+":""}{r.averageOpponentRating.toFixed(1)}</td><td>{r.recentForm>0?"+":""}{r.recentForm.toFixed(1)}</td></tr>)}</tbody></table>
   {b.rankings.length>10?<button className="linkButton" onClick={()=>setAll(v=>!v)}>{all?"Show top 10":"Show all "+b.rankings.length}</button>:null}
   <p className="feedNote">{b.provider}{b.fallback?" · FALLBACK":""} · older games count less (recency half-life). {b.notes[b.notes.length-1]}</p>
  </>}
 </section>;
}
