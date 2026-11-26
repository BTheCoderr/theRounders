"use client";
import {useEffect,useState} from "react";
import {pct} from "../lib/clientTypes";
import {nickname} from "../lib/teams";
import type {Sport} from "../lib/sports";

type Pick={eventId:string;startsAt:string;home:string;away:string;side:string;kind:"spread"|"moneyline";edge:number;modelLine:number;marketLine:number;lineSource:string|null;result:"win"|"loss"|"push"|null};
type Data={ready:boolean;reason?:string;threshold:{kind:"points"|"probability";value:number};upcoming:Pick[];recent:Pick[];
 record:{picks:number;wins:number;losses:number;pushes:number;winRate:number|null;breakEven:number|null};gradedWithLine:number};
const when=(iso:string)=>new Date(iso).toLocaleString([],{weekday:"short",hour:"numeric",minute:"2-digit"});
const line=(p:Pick,sport:Sport)=>p.kind==="spread"
 ?`${nickname(p.side,sport)} ${(()=>{const s=p.side===p.home?p.marketLine:-p.marketLine;return s>0?"+"+s:String(s)})()}`
 :`${nickname(p.side,sport)} ML`;
const why=(p:Pick)=>p.kind==="spread"?`${p.edge} pts vs market`:`${p.modelLine}% vs market ${p.marketLine}%`;

export default function EdgePicks({sport}:{sport:Sport}){
 const [d,setD]=useState<Data|null>(null),[err,setErr]=useState("");
 useEffect(()=>{
  const c=new AbortController();setD(null);setErr("");
  fetch("/api/edge-picks?sport="+sport,{signal:c.signal}).then(r=>r.json()).then((x:Data)=>{if(c.signal.aborted)return;x.ready?setD(x):setErr(x.reason||"Edge picks are unavailable.")})
   .catch(()=>{if(!c.signal.aborted)setErr("Edge picks are unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 if(err)return null;
 const t=d?.threshold,rec=d?.record;
 return <section className="block">
  <div className="blockHead"><h2>{sport} edge picks</h2><span className="chip free">BETA</span></div>
  {!d?<div className="statStrip skeleton"/>:<>
   <p className="fine">Locked picks where our line differs from the market by {t!.kind==="points"?`${t!.value}+ points`:`${Math.round(t!.value*100)}+ points of win probability`}. The threshold was set in advance.</p>
   <div className="statStrip">
    <div><small>Edge record</small><strong>{rec!.wins}-{rec!.losses}{rec!.pushes?`-${rec!.pushes}`:""}</strong><span>{t!.kind==="points"?"against the spread":"straight up"}</span></div>
    <div><small>Win %</small><strong>{pct(rec!.winRate,1)}</strong><span>{rec!.breakEven!==null?`break-even ${pct(rec!.breakEven,1)}`:"—"}</span></div>
    <div><small>Open edges</small><strong>{d.upcoming.length}</strong><span>upcoming</span></div>
    <div><small>Graded with a line</small><strong>{d.gradedWithLine}</strong><span>games</span></div>
   </div>
   {!rec!.picks&&!d.upcoming.length?<p className="empty">No edge picks yet. Market lines started recording on Nov 26, so this fills in as games are played.</p>:
   <ul className="ledger">{[...d.upcoming,...d.recent.slice(0,15)].map(p=><li key={p.eventId}>
    <div className="lgMain"><span className="lgGame">{nickname(p.away,sport)} @ {nickname(p.home,sport)}</span><span className="lgMeta">{when(p.startsAt)} · {p.lineSource}</span></div>
    <div className="lgPick"><small>Edge</small><b>{line(p,sport)}</b><span>{why(p)}</span></div>
    <span className={"lgMark "+(p.result==="win"?"pos":p.result==="loss"?"neg":"")}>{p.result==="win"?"✓":p.result==="loss"?"✗":p.result==="push"?"–":"•"}</span>
   </li>)}</ul>}
  </>}
 </section>;
}
