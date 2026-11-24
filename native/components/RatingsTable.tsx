"use client";
import {useEffect,useMemo,useState} from "react";
import {nickname,onColor,team} from "../lib/teams";
import {useSport} from "./useSport";
import SportBar from "./SportBar";

type Row={rank:number;change:number|null;team:string;slug:string;wins:number;losses:number;ties:number;games:number;
 rating:number;offense:number|null;defense:number|null;sos:number|null;last10:{wins:number;losses:number};streak:string;
 pointsFor:number|null;pointsAgainst:number|null};
type Table={ready:boolean;reason?:string;sport:string;season:number;asOf:string;games:number;homeAdvantage:number;leaguePoints:number|null;rows:Row[];notes?:string[]};
type Key="rank"|"rating"|"offense"|"defense"|"sos"|"record"|"change";
const COLS:Array<{key:Key;label:string;title:string}>=[
 {key:"rank",label:"Rk",title:"Power Index rank"},{key:"record",label:"W-L",title:"This season's record"},
 {key:"rating",label:"Rating",title:"Points better than an average team on a neutral site"},
 {key:"offense",label:"Off",title:"Points scored above average vs an average defense"},
 {key:"defense",label:"Def",title:"Points allowed below average vs an average offense (higher is better)"},
 {key:"sos",label:"SoS",title:"Average rating of opponents faced this season"},
 {key:"change",label:"7d",title:"Rank change over the last seven days"}
];
const sgn=(x:number|null,d=1)=>x===null?"—":(x>0?"+":"")+x.toFixed(d);
const value=(r:Row,k:Key)=>k==="record"?(r.wins+r.ties/2)/Math.max(1,r.games):k==="rank"?-r.rank:(r[k]??-999);

export default function RatingsTable(){
 const [sport,setSport]=useSport();
 const [t,setT]=useState<Table|null>(null),[error,setError]=useState(""),[sort,setSort]=useState<{key:Key;desc:boolean}>({key:"rank",desc:true});
 useEffect(()=>{
  const c=new AbortController();setT(null);setError("");
  fetch("/api/team-ratings?sport="+sport,{signal:c.signal})
   .then(async r=>{const x=await r.json() as Table;if(c.signal.aborted)return;if(!x.ready)setError(x.reason||"Ratings are unavailable right now.");else setT(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Ratings are unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const rows=useMemo(()=>t?[...t.rows].sort((a,b)=>(value(b,sort.key)-value(a,sort.key))*(sort.desc?1:-1)||a.rank-b.rank):[],[t,sort]);
 const click=(key:Key)=>setSort(s=>({key,desc:s.key===key?!s.desc:true}));
 return <>
  <SportBar sport={sport} onChange={setSport}/>
  <section className="block">
   <div className="blockHead"><h2>{sport} ratings{t?" · "+(sport==="NBA"?`${t.season}–${String(t.season+1).slice(2)}`:t.season):""}</h2><span className="chip free">FREE</span></div>
   {error?<p className="empty">{error}</p>:!t?<div className="rankList skeleton"/>:<>
    <p className="swipeHint">Swipe the table for offense, defense and schedule →</p>
    <div className="tableWrap"><table className="ratingsTable">
     <thead><tr><th className="teamCol">Team</th>{COLS.map(c=><th key={c.key} title={c.title} aria-sort={sort.key===c.key?(sort.desc?"descending":"ascending"):"none"}>
      <button onClick={()=>click(c.key)}>{c.label}{sort.key===c.key?(sort.desc?" ↓":" ↑"):""}</button></th>)}</tr></thead>
     <tbody>{rows.map(r=>{const b=team(sport,r.team);return <tr key={r.team}>
      <td className="teamCol"><a href={`/teams/${sport.toLowerCase()}/${r.slug}`}>
       <span className="teamBadge sm" style={{background:b.color,color:onColor(b.color)}} aria-hidden="true">{b.abbr}</span>
       <span className="full">{r.team}</span><span className="short">{nickname(r.team)}</span></a></td>
      <td className="num">{r.rank}</td>
      <td className="num">{r.wins}-{r.losses}{r.ties?"-"+r.ties:""}</td>
      <td className={"num strong "+(r.rating>=0?"pos":"neg")}>{sgn(r.rating)}</td>
      <td className="num">{sgn(r.offense)}</td>
      <td className="num">{sgn(r.defense)}</td>
      <td className="num">{sgn(r.sos)}</td>
      <td className={"num "+(r.change&&r.change>0?"pos":r.change&&r.change<0?"neg":"")}>{r.change===null||r.change===0?"–":(r.change>0?"▲":"▼")+Math.abs(r.change)}</td>
     </tr>})}</tbody>
    </table></div>
    <p className="fine">Rating = points better than an average team on a neutral site, adjusted for opponents and weighted toward recent games. Home edge {t.homeAdvantage.toFixed(1)} pts{t.leaguePoints?` · league average ${(t.leaguePoints).toFixed(1)} pts per team`:""} · {t.games} games this season · updated {new Date(t.asOf).toLocaleString([],{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"})}.</p>
    {t.notes?.length?<p className="fine">{t.notes.join(" ")}</p>:null}
   </>}
  </section>
 </>;
}
