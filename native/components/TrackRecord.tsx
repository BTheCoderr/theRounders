"use client";
import {useEffect,useState} from "react";
import {num,pct,type Summary} from "../lib/clientTypes";
import {nickname} from "../lib/teams";
import {useSport} from "./useSport";
import SportBar from "./SportBar";

type Pick={eventId:string;startsAt:string;predictedAt:string;home:string;away:string;winner:string;probability:number;
 projectedSpreadHome:number;projectedTotal:number;final:{home:number|null;away:number|null};correct:boolean|null;marginError:number|null};
type Data={ready:boolean;reason?:string;modelLabel:string;summary:Summary;picks:Pick[];notes:string[]};
const when=(iso:string)=>new Date(iso).toLocaleString([],{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});

export default function TrackRecord(){
 const [sport,setSport]=useSport();
 const [d,setD]=useState<Data|null>(null),[error,setError]=useState(""),[filter,setFilter]=useState<"all"|"right"|"wrong">("all");
 useEffect(()=>{
  const c=new AbortController();setD(null);setError("");
  fetch("/api/track-record?sport="+sport,{signal:c.signal,cache:"no-store"})
   .then(async r=>{const x=await r.json() as Data;if(c.signal.aborted)return;if(!x.ready)setError(x.reason||"Track record is unavailable.");else setD(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Track record is unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const s=d?.summary;
 const picks=d?d.picks.filter(p=>filter==="all"||(filter==="right"?p.correct===true:p.correct===false)):[];
 return <>
  <SportBar sport={sport} onChange={setSport}/>
  <section className="block">
   <div className="blockHead"><h2>{sport} ledger</h2><span className="chip free">FREE</span></div>
   {error?<p className="empty">{error}</p>:!d||!s?<div className="statStrip skeleton"/>:!d.picks.length?
    <div className="emptyRecord"><b>The ledger starts with the first graded slate.</b><span>Every {sport} pick is stored before the game and added here after the final, right or wrong.</span></div>:<>
    <div className="statStrip">
     <div><small>Record</small><strong>{d.picks.filter(p=>p.correct).length}-{d.picks.filter(p=>p.correct===false).length}</strong><span>straight up</span></div>
     <div><small>Accuracy</small><strong>{pct(s.winnerAccuracy,1)}</strong><span>{s.decided} decided</span></div>
     <div><small>Brier</small><strong>{num(s.brierScore,3)}</strong><span>0.250 = coin flip</span></div>
     <div><small>Spread error</small><strong>{num(s.marginMAE,1)}</strong><span>points</span></div>
    </div>
    <div className="marketTabs" role="tablist">{(["all","right","wrong"] as const).map(f=><button key={f} role="tab" aria-selected={filter===f} className={filter===f?"active":""} onClick={()=>setFilter(f)}>{f==="all"?"All":f==="right"?"Hits":"Misses"}</button>)}</div>
    <ul className="ledger">{picks.map(p=><li key={p.eventId}>
     <div className="lgMain"><span className="lgGame">{nickname(p.away,sport)} @ {nickname(p.home,sport)}</span>
      <span className="lgMeta">{when(p.startsAt)} · locked {when(p.predictedAt)}</span></div>
     <div className="lgPick"><small>Pick</small><b>{nickname(p.winner,sport)} {pct(p.probability,0)}</b><span>{p.projectedSpreadHome>0?nickname(p.away,sport):nickname(p.home,sport)} {(-Math.abs(p.projectedSpreadHome)).toFixed(1)} · O/U {p.projectedTotal.toFixed(1)}</span></div>
     <div className="lgFinal"><small>Final</small><b>{p.final.away}-{p.final.home}</b></div>
     <span className={"lgMark "+(p.correct?"pos":p.correct===false?"neg":"")} aria-label={p.correct?"Correct":p.correct===false?"Wrong":"Tie"}>{p.correct?"✓":p.correct===false?"✗":"–"}</span>
    </li>)}</ul>
   </>}
   {d?.notes?.length?<p className="fine">{d.notes.join(" ")} Model: {d.modelLabel}.</p>:null}
  </section>
 </>;
}
