"use client";
import {useEffect,useState} from "react";
import {num,pct,type Summary} from "../lib/clientTypes";
import {nickname} from "../lib/teams";
import {useSport} from "./useSport";
import SportBar from "./SportBar";
import EdgePicks from "./EdgePicks";

type Pick={eventId:string;startsAt:string;predictedAt:string;home:string;away:string;winner:string;probability:number;
 projectedSpreadHome:number;projectedTotal:number;final:{home:number|null;away:number|null};correct:boolean|null;marginError:number|null};
type Overall={ready:boolean;wins:number;losses:number;winRate:number|null;strong?:{wins:number;losses:number;winRate:number|null};bySport:Array<{sport:string;wins:number;losses:number;winRate:number|null}>};
type Data={ready:boolean;reason?:string;modelLabel:string;summary:Summary;picks:Pick[];notes:string[]};
const when=(iso:string)=>new Date(iso).toLocaleString([],{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});

export default function TrackRecord(){
 const [sport,setSport]=useSport();
 const [all,setAll]=useState<Overall|null>(null);
 useEffect(()=>{
  const c=new AbortController();
  fetch("/api/track-record?sport=ALL",{signal:c.signal}).then(r=>r.json()).then((x:Overall)=>{if(!c.signal.aborted&&x.ready)setAll(x)}).catch(()=>{});
  return()=>c.abort();
 },[]);
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
  {all&&all.wins+all.losses>0?<section className="block">
   <div className="blockHead"><h2>All sports</h2></div>
   <div className="statStrip">
    <div><small>Overall record</small><strong>{all.wins}-{all.losses}</strong><span>straight up</span></div>
    <div><small>Win %</small><strong>{pct(all.winRate,1)}</strong><span>{all.wins+all.losses} decided</span></div>
    {all.strong&&all.strong.wins+all.strong.losses>0?<div><small>Strong picks (70%+)</small><strong>{all.strong.wins}-{all.strong.losses}</strong><span>{pct(all.strong.winRate,1)}</span></div>:null}
    {all.bySport.filter(x=>x.wins+x.losses>0).map(x=><div key={x.sport}><small>{x.sport}</small><strong>{x.wins}-{x.losses}</strong><span>{pct(x.winRate,1)}</span></div>)}
   </div>
  </section>:null}
  <SportBar sport={sport} onChange={setSport}/>
  <EdgePicks sport={sport}/>
  <section className="block">
   <div className="blockHead"><h2>{sport} ledger</h2><span className="chip free">FREE</span></div>
   {error?<p className="empty">{error}</p>:!d||!s?<div className="statStrip skeleton"/>:!d.picks.length?
    <div className="emptyRecord"><b>The ledger starts with the first graded slate.</b><span>Every {sport} pick is stored before the game and added here after the final, right or wrong.</span></div>:<>
    <div className="statStrip">
     <div><small>Record</small><strong>{d.picks.filter(p=>p.correct).length}-{d.picks.filter(p=>p.correct===false).length}</strong><span>straight up</span></div>
     <div><small>Accuracy</small><strong>{pct(s.winnerAccuracy,1)}</strong><span>{s.decided} decided</span></div>
     {(()=>{const st=d.picks.filter(p=>p.probability>=0.7&&p.correct!==null);const w=st.filter(p=>p.correct).length;
      return st.length?<div><small>Strong picks (70%+)</small><strong>{w}-{st.length-w}</strong><span>{pct(w/st.length,1)}</span></div>:null;})()}
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
