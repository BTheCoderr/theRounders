"use client";
import {useEffect,useMemo,useState} from "react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import {nickname,onColor,team} from "../lib/teams";
import {SPORT_NAME,UNIT,type ProductSport} from "../lib/clientTypes";
import SportBar from "./SportBar";

type Row={rank:number;change:number|null;team:string;slug:string;wins:number;losses:number;ties:number;games:number;
 rating:number;offense:number|null;defense:number|null;sos:number|null;last10:{wins:number;losses:number};streak:string;
 pointsFor:number|null;pointsAgainst:number|null;remaining?:number;projWins?:number;projLosses?:number};
export type RatingsTableData={projected?:boolean;historical?:boolean;seasons?:number[];ready:boolean;reason?:string;sport:string;season:number;asOf:string;games:number;homeAdvantage:number;leaguePoints:number|null;rows:Row[];notes?:string[]};
type Key="rank"|"rating"|"offense"|"defense"|"sos"|"record"|"change"|"proj";
const COLS:Array<{key:Key;label:string;title:string}>=[
 {key:"rank",label:"Rk",title:"Power Index rank"},{key:"record",label:"W-L",title:"This season's record"},
 {key:"proj",label:"Proj",title:"Projected final record: current record plus each remaining game's win probability"},
 {key:"rating",label:"Rating",title:"Points better than an average team on a neutral site"},
 {key:"offense",label:"Off",title:"Points scored above average vs an average defense"},
 {key:"defense",label:"Def",title:"Points allowed below average vs an average offense (higher is better)"},
 {key:"sos",label:"SoS",title:"Average rating of opponents faced this season"},
 {key:"change",label:"7d",title:"Rank change over the last seven days"}
];
export const seasonLabel=(s:ProductSport,y:number)=>s==="NFL"||s==="NCAAF"||s==="MLB"?String(y):`${y}–${String(y+1).slice(2)}`;
const sgn=(x:number|null,d=1)=>x===null?"—":(x>0?"+":"")+x.toFixed(d);
const value=(r:Row,k:Key)=>k==="proj"?(r.projWins??-1):k==="record"?(r.wins+r.ties/2)/Math.max(1,r.games):k==="rank"?-r.rank:(r[k]??-999);

/**
 * Server pages pass the sport (from the URL) and the data they already loaded, so the
 * table is in the HTML search engines see. Switching sport or season navigates to that
 * page; the client only fetches itself if the server had nothing (e.g. data still loading).
 */
export default function RatingsTable({sport,initial,historical=false}:{sport:ProductSport;initial:RatingsTableData|null;historical?:boolean}){
 const router=useRouter();
 const [t,setT]=useState<RatingsTableData|null>(initial),[error,setError]=useState(""),[sort,setSort]=useState<{key:Key;desc:boolean}>({key:"rank",desc:true});
 const base=historical?"/history/":"/ratings/";
 useEffect(()=>{try{localStorage.setItem("rounders.sport",sport)}catch{/* not persisted */}},[sport]);
 useEffect(()=>{
  setT(initial);setError("");
  if(initial)return;
  const c=new AbortController();
  fetch(historical?`/api/history?sport=${sport}`:"/api/team-ratings?sport="+sport,{signal:c.signal})
   .then(async r=>{const x=await r.json() as RatingsTableData;if(c.signal.aborted)return;
    if(!x.ready)setError(x.reason||"Ratings are unavailable right now.");else setT(x);})
   .catch(()=>{if(!c.signal.aborted)setError("Ratings are unavailable right now.")});
  return()=>c.abort();
 },[sport,historical,initial]);
 const seasons=t?.seasons||[];
 const pickSport=(s:ProductSport)=>router.push(base+s.toLowerCase());
 const dp=UNIT[sport]==="pts"?1:2;
 const rows=useMemo(()=>t?[...t.rows].sort((a,b)=>(value(b,sort.key)-value(a,sort.key))*(sort.desc?1:-1)||a.rank-b.rank):[],[t,sort]);
 const click=(key:Key)=>setSort(s=>({key,desc:s.key===key?!s.desc:true}));
 return <>
  <SportBar sport={sport} onChange={pickSport}/>
  {historical&&seasons.length?<label className="seasonPick">Season <select value={t?.season??""} onChange={e=>router.push(`/history/${sport.toLowerCase()}/${e.target.value}`)}>
   {seasons.map(y=><option key={y} value={y}>{seasonLabel(sport,y)}</option>)}</select></label>:null}
  <section className="block">
   <div className="blockHead"><h2>{SPORT_NAME[sport]} {t?.historical?"final ratings":"ratings"}{t?" · "+seasonLabel(sport,t.season):""}</h2><span className="chip free">FREE</span></div>
   {error?<p className="empty">{error}</p>:!t?<div className="rankList skeleton"/>:<>
    <p className="swipeHint">Swipe the table for offense, defense and schedule →</p>
    <div className="tableWrap"><table className="ratingsTable">
     <thead><tr><th className="teamCol">Team</th>{COLS.filter(c=>(c.key!=="proj"||t.projected)&&(c.key!=="change"||!t.historical)).map(c=><th key={c.key} title={c.title} aria-sort={sort.key===c.key?(sort.desc?"descending":"ascending"):"none"}>
      <button onClick={()=>click(c.key)}>{c.label}{sort.key===c.key?(sort.desc?" ↓":" ↑"):""}</button></th>)}</tr></thead>
     <tbody>{rows.map(r=>{const b=team(sport,r.team);return <tr key={r.team}>
      <td className="teamCol">{t.historical?<span className="teamCell">
       <span className="teamBadge sm" style={{background:b.color,color:onColor(b.color)}} aria-hidden="true">{b.abbr}</span>
       <span className="full">{r.team}</span><span className="short">{nickname(r.team,sport)}</span></span>:<Link href={`/teams/${sport.toLowerCase()}/${r.slug}`}>
       <span className="teamBadge sm" style={{background:b.color,color:onColor(b.color)}} aria-hidden="true">{b.abbr}</span>
       <span className="full">{r.team}</span><span className="short">{nickname(r.team,sport)}</span></Link>}</td>
      <td className="num">{r.rank}</td>
      <td className="num">{r.wins}-{r.losses}{r.ties?"-"+r.ties:""}</td>
      {t.projected?<td className="num proj" title={`${r.remaining??0} games left`}>{r.projWins!==undefined?`${Math.round(r.projWins)}-${Math.round(r.projLosses??0)}`:"—"}</td>:null}
      <td className={"num strong "+(r.rating>=0?"pos":"neg")}>{sgn(r.rating,dp)}</td>
      <td className="num">{sgn(r.offense,dp)}</td>
      <td className="num">{sgn(r.defense,dp)}</td>
      <td className="num">{sgn(r.sos,dp)}</td>
{t.historical?null:<td className={"num "+(r.change&&r.change>0?"pos":r.change&&r.change<0?"neg":"")}>{r.change===null||r.change===0?"–":(r.change>0?"▲":"▼")+Math.abs(r.change)}</td>}
     </tr>})}</tbody>
    </table></div>
    <p className="fine">Rating = how much better than an average team on a neutral site, adjusted for opponents and weighted toward recent games. Ratings in {UNIT[sport]}. Home edge {t.homeAdvantage.toFixed(t.homeAdvantage<1?2:1)} {UNIT[sport]}{t.leaguePoints?` · league average ${(t.leaguePoints).toFixed(1)} ${UNIT[sport]} per team`:""}{t.projected?" · Proj = projected final record":""} · {t.games} games{t.historical?"":" this season · updated"} {t.historical?"":new Date(t.asOf).toLocaleString("en-US",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit",timeZone:"America/New_York",timeZoneName:"short"})}.</p>
    {t.notes?.length?<p className="fine">{t.notes.join(" ")}</p>:null}
   </>}
  </section>
 </>;
}
