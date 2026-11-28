"use client";
import {useEffect,useState} from "react";
import {num,pct} from "../lib/clientTypes";
import type {Sport} from "../lib/sports";

type Score={label:string;games:number;su:{wins:number;losses:number;winRate:number|null};ats:{wins:number;losses:number;pushes:number;winRate:number|null}|null;brier:number|null;mae:number|null};
type Data={ready:boolean;games:number;models:Score[];market:Score};
export default function Scorecard({sport}:{sport:Sport}){
 const [d,setD]=useState<Data|null>(null);
 useEffect(()=>{const c=new AbortController();setD(null);
  fetch("/api/scorecard?sport="+sport,{signal:c.signal}).then(r=>r.json()).then((x:Data)=>{if(!c.signal.aborted&&x.ready)setD(x)}).catch(()=>{});
  return()=>c.abort();},[sport]);
 if(!d)return null;
 const rows=[...d.models,d.market];
 return <section className="block">
  <div className="blockHead"><h2>{sport} model scorecard</h2><span className="chip free">SAME GAMES</span></div>
  {!d.games?<p className="empty">The head-to-head starts once games with both picks and a captured line are graded.</p>:<>
  <p className="fine">{d.games} graded games where every model locked a pick and a line was captured. Against the spread needs 52.4% to break even.</p>
  <div className="tableWrap"><table className="scoreTable">
   <thead><tr><th>Model</th><th>Straight up</th><th>Against the spread</th><th>Brier</th><th>Avg miss</th></tr></thead>
   <tbody>{rows.map(r=><tr key={r.label}><td>{r.label}</td>
    <td>{r.su.wins}-{r.su.losses} <small>{pct(r.su.winRate,1)}</small></td>
    <td>{r.ats?<>{r.ats.wins}-{r.ats.losses}{r.ats.pushes?`-${r.ats.pushes}`:""} <small>{pct(r.ats.winRate,1)}</small></>:"—"}</td>
    <td>{num(r.brier,3)}</td><td>{num(r.mae,1)}</td></tr>)}</tbody>
  </table></div></>}
 </section>;
}
