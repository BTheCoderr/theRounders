"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import {pct,SPORT_NAME,UNIT,isProductSport} from "../lib/clientTypes";
import {nickname,onColor,team as teamStyle} from "../lib/teams";

type Pick={winner:string;teamWinProbability:number;correct:boolean|null;predictedAt:string;pickedTeam:boolean|null};
type Result={date:string;opponent:string;opponentRank:number|null;home:boolean;neutral:boolean;pf:number;pa:number;result:"W"|"L"|"T";pick:Pick|null};
type Upcoming={startsAt:string;opponent:string;opponentRank:number|null;home:boolean;neutral:boolean;winner:string;teamWinProbability:number;predictedAt:string};
export type TeamData={ready:boolean;reason?:string;sport:string;season:number;teams:number;homeAdvantage:number;modelLabel:string;
 team:{rank:number;team:string;wins:number;losses:number;ties:number;rating:number;offense:number|null;defense:number|null;sos:number|null;
  last10:{wins:number;losses:number};streak:string;pointsFor:number|null;pointsAgainst:number|null;remaining?:number;projWins?:number;projLosses?:number};
 history:Array<{date:string;rating:number;rank:number}>;results:Result[];upcoming:Upcoming[]};
const sgn=(x:number|null,d=1)=>x===null?"—":(x>0?"+":"")+x.toFixed(d);
// Fixed to US Eastern so the server-rendered HTML and the browser agree.
const ET={timeZone:"America/New_York"} as const;
const day=(iso:string)=>new Date(iso).toLocaleDateString("en-US",{month:"short",day:"numeric",...ET});
const kickoff=(iso:string)=>new Date(iso).toLocaleString("en-US",{weekday:"short",month:"short",day:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short",...ET});

function Trend({h,dp}:{h:TeamData["history"];dp:number}){
 if(h.length<2)return <p className="fine">The rating trend appears after the team&apos;s second week.</p>;
 const W=320,H=90,P=8;
 const vals=h.map(x=>x.rating),lo=Math.min(0,...vals),hi=Math.max(0,...vals),span=Math.max(1,hi-lo);
 const x=(i:number)=>P+i*(W-2*P)/(h.length-1),y=(v:number)=>P+(hi-v)*(H-2*P)/span;
 const d=h.map((p,i)=>(i?"L":"M")+x(i).toFixed(1)+" "+y(p.rating).toFixed(1)).join(" ");
 const last=h[h.length-1];
 return <figure className="trend">
  <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Rating trend, now ${sgn(last.rating,dp)}, rank ${last.rank}`}>
   <line x1={P} x2={W-P} y1={y(0)} y2={y(0)} className="zero"/>
   <path d={d} className="line"/>
   {h.map((p,i)=><circle key={p.date} cx={x(i)} cy={y(p.rating)} r={i===h.length-1?3.5:2} className="dot"><title>{day(p.date)}: {sgn(p.rating,dp)} (#{p.rank})</title></circle>)}
  </svg>
  <figcaption><span>{day(h[0].date)}</span><span>Rating by week · dashed line = average team</span><span>Now</span></figcaption>
 </figure>;
}

/** The server page passes `initial`, so the team page is in the HTML; the client only fetches as a fallback. */
export default function TeamPage({sport,slug,initial}:{sport:string;slug:string;initial:TeamData|null}){
 const [d,setD]=useState<TeamData|null>(initial),[error,setError]=useState("");
 useEffect(()=>{
  if(initial)return;
  const c=new AbortController();
  fetch(`/api/team?sport=${encodeURIComponent(sport)}&team=${encodeURIComponent(slug)}`,{signal:c.signal})
   .then(async r=>{const x=await r.json() as TeamData;if(c.signal.aborted)return;if(!x.ready)setError(x.reason||"Team data is unavailable.");else setD(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Team data is unavailable right now.")});
  return()=>c.abort();
 },[sport,slug,initial]);
 if(error)return <main className="home"><p className="empty" style={{marginTop:24}}>{error} <Link href={"/ratings/"+sport.toLowerCase()}>All {sport} ratings</Link></p></main>;
 if(!d)return <main className="home"><div className="statStrip skeleton" style={{marginTop:24}}/></main>;
 const t=d.team,b=teamStyle(sport,t.team);
 const sp=isProductSport(sport)?sport:"NBA",unit=UNIT[sp],dp=unit==="pts"?1:2;
 const picked=d.results.filter(r=>r.pick&&r.pick.correct!==null);
 const right=picked.filter(r=>r.pick!.correct).length;
 const tiles:[string,string,string][]=[
  ["Rating",sgn(t.rating,dp),unit+" vs average"],["Offense",sgn(t.offense,dp),unit+"/game"],["Defense",sgn(t.defense,dp),unit+"/game"],
  t.projWins!==undefined?["Projected",`${Math.round(t.projWins)}-${Math.round(t.projLosses??0)}`,`${t.remaining??0} games left`]:["SoS",sgn(t.sos,dp),"opponents"]
 ];
 return <main className="home teamPage">
  <Link className="back" href={"/ratings/"+sport.toLowerCase()}>← {SPORT_NAME[sp]} ratings</Link>
  <section className="teamHero">
   <span className="teamBadge xl" style={{background:b.color,color:onColor(b.color)}} aria-hidden="true">{b.abbr}</span>
   <div><p className="eyebrow">#{t.rank} OF {d.teams} · {SPORT_NAME[sp].toUpperCase()}</p><h1>{t.team}</h1>
    <p className="heroSub">{t.wins}-{t.losses}{t.ties?"-"+t.ties:""} · last 10 {t.last10.wins}-{t.last10.losses}{t.streak?" · streak "+t.streak:""}{t.pointsFor!==null?` · ${t.pointsFor.toFixed(1)}–${t.pointsAgainst!.toFixed(1)} avg score`:""}{t.sos!==null&&t.projWins!==undefined?` · SoS ${sgn(t.sos,dp)}`:""}</p></div>
  </section>
  <div className="statStrip">{tiles.map(([a,v,c])=><div key={a}><small>{a}</small><strong>{v}</strong><span>{c}</span></div>)}</div>
  <section className="block"><div className="blockHead"><h2>Rating trend</h2></div><Trend h={d.history} dp={dp}/></section>
  {d.upcoming.length?<section className="block"><div className="blockHead"><h2>Next up</h2><span className="chip free">FREE</span></div>
   <ul className="sched">{d.upcoming.map(u=><li key={u.startsAt+u.opponent}>
    <span className="when">{kickoff(u.startsAt)}</span>
    <span className="opp">{u.neutral?"vs":u.home?"vs":"@"} {nickname(u.opponent,sport)}{u.opponentRank?<small> #{u.opponentRank}</small>:null}</span>
    <span className={"pickCell "+(u.winner===t.team?"pos":"neg")}>{nickname(u.winner,sport)} {pct(u.winner===t.team?u.teamWinProbability:1-u.teamWinProbability,0)}</span>
   </li>)}</ul>
   <p className="fine">Picks locked {day(d.upcoming[0].predictedAt)} by {d.modelLabel}. Spreads and totals are on the <Link href="/#predictions">picks board</Link>.</p>
  </section>:null}
  <section className="block"><div className="blockHead"><h2>{sp==="NFL"||sp==="NCAAF"||sp==="MLB"?d.season:`${d.season}–${String(d.season+1).slice(2)}`} results</h2>{picked.length?<span className="chip">{right}-{picked.length-right} PICKS</span>:null}</div>
   {!d.results.length?<p className="empty">No games yet this season.</p>:<ul className="sched">{d.results.map(r=><li key={r.date+r.opponent}>
    <span className="when">{day(r.date)}</span>
    <span className="opp">{r.neutral?"vs":r.home?"vs":"@"} {nickname(r.opponent,sport)}{r.opponentRank?<small> #{r.opponentRank}</small>:null}</span>
    <span className={"score "+(r.result==="W"?"pos":r.result==="L"?"neg":"")}>{r.result} {r.pf}-{r.pa}</span>
    <span className="pickCell">{r.pick?<>{nickname(r.pick.winner,sport)} {pct(r.pick.pickedTeam?r.pick.teamWinProbability:1-r.pick.teamWinProbability,0)} <b className={r.pick.correct?"pos":"neg"}>{r.pick.correct?"✓":"✗"}</b></>:<small>no stored pick</small>}</span>
   </li>)}</ul>}
   <p className="fine">Pick column: the {d.modelLabel} pick stored before tip-off/kickoff. Games before our live record started have no stored pick.</p>
  </section>
 </main>;
}
